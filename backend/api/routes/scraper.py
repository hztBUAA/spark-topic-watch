from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from pydantic import BaseModel
from core.database import get_db, ScrapingLog, UserConfig
from services.scraper_service import scraper_service
from services.analysis_service import analysis_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class SearchRequest(BaseModel):
    keywords: List[str]
    limit: Optional[int] = 20

class AnalyzeRequest(BaseModel):
    url: str

@router.post("/login")
async def login():
    """登录小红书账号"""
    try:
        result = await scraper_service.login()
        
        return {
            "success": True,
            "message": result
        }
        
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

@router.post("/search")
async def manual_search(
    request: SearchRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """手动触发搜索"""
    try:
        # 添加后台任务进行数据采集
        background_tasks.add_task(
            _background_collect,
            request.keywords,
            request.limit,
            db
        )
        
        return {
            "success": True,
            "message": "搜索任务已启动",
            "data": {
                "keywords": request.keywords,
                "limit": request.limit,
                "status": "started"
            }
        }
        
    except Exception as e:
        logger.error(f"启动搜索任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动搜索任务失败: {str(e)}")

async def _background_collect(keywords: List[str], limit: int, db: AsyncSession):
    """后台采集任务"""
    try:
        # 执行批量采集
        results = await scraper_service.batch_collect_data(keywords, db)
        
        # 更新词云和情绪分析数据
        for keyword in keywords:
            await analysis_service.update_word_cloud_data(keyword, db)
            await analysis_service.update_sentiment_analysis(keyword, db)
        
        logger.info(f"后台采集完成: {results}")
        
    except Exception as e:
        logger.error(f"后台采集失败: {str(e)}")

@router.post("/analyze")
async def analyze_note(
    request: AnalyzeRequest,
    db: AsyncSession = Depends(get_db)
):
    """分析指定笔记"""
    try:
        # 记录开始分析
        log = ScrapingLog(
            task_type="analyze",
            keyword="",
            status="running",
            message=f"开始分析笔记: {request.url}"
        )
        db.add(log)
        await db.commit()
        
        try:
            # 获取笔记内容
            content = await scraper_service.get_note_content(request.url)
            
            # 更新日志
            log.status = "success"
            log.message = "分析完成"
            log.data_count = 1
            await db.commit()
            
            return {
                "success": True,
                "data": content,
                "url": request.url
            }
            
        except Exception as e:
            # 更新日志
            log.status = "failed"
            log.message = f"分析失败: {str(e)}"
            await db.commit()
            raise e
            
    except Exception as e:
        logger.error(f"分析笔记失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析笔记失败: {str(e)}")

@router.get("/logs")
async def get_scraping_logs(
    limit: int = 20,
    task_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取采集日志"""
    try:
        query = select(ScrapingLog).order_by(desc(ScrapingLog.started_at)).limit(limit)
        
        if task_type:
            query = query.where(ScrapingLog.task_type == task_type)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        log_data = []
        for log in logs:
            log_data.append({
                "id": log.id,
                "task_type": log.task_type,
                "keyword": log.keyword,
                "status": log.status,
                "message": log.message,
                "data_count": log.data_count,
                "started_at": log.started_at.isoformat(),
                "completed_at": log.completed_at.isoformat() if log.completed_at else None
            })
        
        return {
            "success": True,
            "data": log_data,
            "total": len(log_data)
        }
        
    except Exception as e:
        logger.error(f"获取采集日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取采集日志失败: {str(e)}")

@router.post("/collect-all")
async def collect_all_keywords(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """采集所有配置的关键词"""
    try:
        # 获取用户配置的关键词
        result = await db.execute(
            select(UserConfig).where(UserConfig.user_id == "default")
        )
        user_config = result.scalar_one_or_none()
        
        if not user_config or not user_config.keywords:
            raise HTTPException(status_code=404, detail="未配置关键词")
        
        # 添加后台任务
        background_tasks.add_task(
            _background_collect,
            user_config.keywords,
            50,  # 默认每个关键词采集50条
            db
        )
        
        return {
            "success": True,
            "message": "全量采集任务已启动",
            "data": {
                "keywords": user_config.keywords,
                "total_keywords": len(user_config.keywords),
                "status": "started"
            }
        }
        
    except Exception as e:
        logger.error(f"启动全量采集失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动全量采集失败: {str(e)}")

@router.get("/status")
async def get_scraper_status():
    """获取采集器状态"""
    try:
        status = {
            "browser_ready": scraper_service.browser_context is not None,
            "logged_in": scraper_service.is_logged_in,
            "last_activity": None  # 可以添加最后活动时间
        }
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        logger.error(f"获取采集器状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取采集器状态失败: {str(e)}")

@router.post("/test-connection")
async def test_connection():
    """测试连接"""
    try:
        # 确保浏览器启动
        browser_ready = await scraper_service.ensure_browser()
        
        return {
            "success": True,
            "data": {
                "browser_ready": browser_ready,
                "logged_in": scraper_service.is_logged_in,
                "message": "连接测试完成"
            }
        }
        
    except Exception as e:
        logger.error(f"测试连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试连接失败: {str(e)}")