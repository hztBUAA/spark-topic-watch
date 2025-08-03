from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
from core.database import get_db, UserConfig
from services.websocket_manager import manager
from services.scraper_service import scraper_service
from services.analysis_service import analysis_service
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 监测状态
monitoring_status: Dict[str, Any] = {
    "is_running": False,
    "current_keywords": [],
    "last_update": None,
    "error_count": 0
}

@router.post("/start")
async def start_monitoring(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """启动实时监测"""
    try:
        # 获取配置的关键词
        result = await db.execute(
            select(UserConfig).where(UserConfig.user_id == "default")
        )
        user_config = result.scalar_one_or_none()
        
        if not user_config or not user_config.keywords:
            raise HTTPException(status_code=404, detail="未配置关键词，请先配置监测关键词")
        
        # 检查是否已在运行
        if monitoring_status["is_running"]:
            return {
                "success": True,
                "message": "监测已在运行中",
                "data": monitoring_status
            }
        
        # 启动监测任务
        monitoring_status["is_running"] = True
        monitoring_status["current_keywords"] = user_config.keywords
        monitoring_status["error_count"] = 0
        
        # 添加后台监测任务
        background_tasks.add_task(
            _background_monitoring,
            user_config.keywords,
            user_config.collection_frequency,
            db
        )
        
        # 通知所有连接的客户端
        await manager.broadcast({
            "type": "monitoring_started",
            "data": monitoring_status
        })
        
        return {
            "success": True,
            "message": "实时监测已启动",
            "data": monitoring_status
        }
        
    except Exception as e:
        logger.error(f"启动监测失败: {str(e)}")
        monitoring_status["is_running"] = False
        raise HTTPException(status_code=500, detail=f"启动监测失败: {str(e)}")

@router.post("/stop")
async def stop_monitoring():
    """停止实时监测"""
    try:
        monitoring_status["is_running"] = False
        monitoring_status["current_keywords"] = []
        
        # 通知所有连接的客户端
        await manager.broadcast({
            "type": "monitoring_stopped",
            "data": monitoring_status
        })
        
        return {
            "success": True,
            "message": "实时监测已停止",
            "data": monitoring_status
        }
        
    except Exception as e:
        logger.error(f"停止监测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"停止监测失败: {str(e)}")

@router.get("/status")
async def get_monitoring_status():
    """获取监测状态"""
    try:
        return {
            "success": True,
            "data": monitoring_status
        }
        
    except Exception as e:
        logger.error(f"获取监测状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取监测状态失败: {str(e)}")

async def _background_monitoring(keywords: list, frequency: str, db: AsyncSession):
    """后台监测任务"""
    try:
        # 根据频率设置监测间隔
        interval_map = {
            "realtime": 300,  # 5分钟
            "hourly": 3600,   # 1小时
            "daily": 86400    # 24小时
        }
        interval = interval_map.get(frequency, 3600)
        
        while monitoring_status["is_running"]:
            try:
                logger.info(f"开始监测循环，关键词: {keywords}")
                
                # 执行数据采集
                results = await scraper_service.batch_collect_data(keywords, db)
                
                # 更新分析数据
                for keyword in keywords:
                    await analysis_service.update_word_cloud_data(keyword, db)
                    await analysis_service.update_sentiment_analysis(keyword, db)
                
                # 更新监测状态
                from datetime import datetime
                monitoring_status["last_update"] = datetime.utcnow().isoformat()
                
                # 推送更新通知
                await manager.broadcast({
                    "type": "data_updated",
                    "data": {
                        "keywords": keywords,
                        "results": results,
                        "timestamp": monitoring_status["last_update"]
                    }
                })
                
                # 检查热帖提醒
                await _check_hot_posts_alert(keywords, db)
                
                logger.info(f"监测循环完成，等待 {interval} 秒")
                
                # 等待下一次监测
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"监测循环出错: {str(e)}")
                monitoring_status["error_count"] += 1
                
                # 如果错误太多，停止监测
                if monitoring_status["error_count"] > 5:
                    monitoring_status["is_running"] = False
                    await manager.broadcast({
                        "type": "monitoring_error",
                        "data": {
                            "message": "监测出现多次错误，已自动停止",
                            "error_count": monitoring_status["error_count"]
                        }
                    })
                    break
                
                # 等待后重试
                await asyncio.sleep(60)
        
        logger.info("监测任务结束")
        
    except Exception as e:
        logger.error(f"后台监测任务失败: {str(e)}")
        monitoring_status["is_running"] = False

async def _check_hot_posts_alert(keywords: list, db: AsyncSession):
    """检查热帖提醒"""
    try:
        # 获取配置
        result = await db.execute(
            select(UserConfig).where(UserConfig.user_id == "default")
        )
        user_config = result.scalar_one_or_none()
        
        if not user_config or not user_config.notification_enabled:
            return
        
        threshold = user_config.hot_post_threshold
        
        # 检查每个关键词的热帖
        for keyword in keywords:
            hot_posts = await analysis_service.rank_hot_posts(keyword, 5, db)
            
            # 查找超过阈值的热帖
            hot_alerts = []
            for post in hot_posts:
                if post["hot_score"] > threshold:
                    hot_alerts.append(post)
            
            if hot_alerts:
                # 推送热帖提醒
                await manager.broadcast({
                    "type": "hot_post_alert",
                    "data": {
                        "keyword": keyword,
                        "threshold": threshold,
                        "hot_posts": hot_alerts
                    }
                })
        
    except Exception as e:
        logger.error(f"检查热帖提醒失败: {str(e)}")

@router.post("/update-frequency")
async def update_monitoring_frequency(
    frequency: str,
    db: AsyncSession = Depends(get_db)
):
    """更新监测频率"""
    try:
        valid_frequencies = ["realtime", "hourly", "daily"]
        if frequency not in valid_frequencies:
            raise HTTPException(
                status_code=400,
                detail=f"无效的监测频率，支持: {', '.join(valid_frequencies)}"
            )
        
        # 更新配置
        result = await db.execute(
            select(UserConfig).where(UserConfig.user_id == "default")
        )
        user_config = result.scalar_one_or_none()
        
        if user_config:
            user_config.collection_frequency = frequency
            await db.commit()
        
        return {
            "success": True,
            "message": f"监测频率已更新为: {frequency}",
            "data": {
                "frequency": frequency,
                "restart_required": monitoring_status["is_running"]
            }
        }
        
    except Exception as e:
        logger.error(f"更新监测频率失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新监测频率失败: {str(e)}")

@router.get("/metrics")
async def get_monitoring_metrics():
    """获取监测指标"""
    try:
        metrics = {
            "is_running": monitoring_status["is_running"],
            "keywords_count": len(monitoring_status["current_keywords"]),
            "last_update": monitoring_status["last_update"],
            "error_count": monitoring_status["error_count"],
            "uptime": None,  # 可以添加运行时间计算
            "success_rate": None  # 可以添加成功率计算
        }
        
        return {
            "success": True,
            "data": metrics
        }
        
    except Exception as e:
        logger.error(f"获取监测指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取监测指标失败: {str(e)}")