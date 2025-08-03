from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from core.database import get_db, UserConfig
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class KeywordConfigRequest(BaseModel):
    keywords: List[str]
    collection_frequency: Optional[str] = "hourly"
    hot_post_threshold: Optional[int] = 100
    notification_enabled: Optional[bool] = True

class ScheduleConfigRequest(BaseModel):
    collection_frequency: str  # hourly, daily, realtime
    data_retention_days: Optional[int] = 30
    hot_post_threshold: Optional[int] = 100

@router.post("/keywords")
async def set_keywords(
    config: KeywordConfigRequest,
    db: AsyncSession = Depends(get_db)
):
    """设置监测关键词"""
    try:
        # 查找或创建用户配置
        result = await db.execute(
            select(UserConfig).where(UserConfig.user_id == "default")
        )
        user_config = result.scalar_one_or_none()
        
        if user_config:
            # 更新现有配置
            user_config.keywords = config.keywords
            user_config.collection_frequency = config.collection_frequency
            user_config.hot_post_threshold = config.hot_post_threshold
            user_config.notification_enabled = config.notification_enabled
        else:
            # 创建新配置
            user_config = UserConfig(
                user_id="default",
                keywords=config.keywords,
                collection_frequency=config.collection_frequency,
                hot_post_threshold=config.hot_post_threshold,
                notification_enabled=config.notification_enabled
            )
            db.add(user_config)
        
        await db.commit()
        await db.refresh(user_config)
        
        return {
            "success": True,
            "message": "关键词配置已更新",
            "data": {
                "keywords": user_config.keywords,
                "collection_frequency": user_config.collection_frequency,
                "hot_post_threshold": user_config.hot_post_threshold,
                "notification_enabled": user_config.notification_enabled
            }
        }
        
    except Exception as e:
        logger.error(f"设置关键词配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"设置关键词配置失败: {str(e)}")

@router.get("/keywords")
async def get_keywords(db: AsyncSession = Depends(get_db)):
    """获取监测关键词配置"""
    try:
        result = await db.execute(
            select(UserConfig).where(UserConfig.user_id == "default")
        )
        user_config = result.scalar_one_or_none()
        
        if user_config:
            return {
                "success": True,
                "data": {
                    "keywords": user_config.keywords,
                    "collection_frequency": user_config.collection_frequency,
                    "data_retention_days": user_config.data_retention_days,
                    "hot_post_threshold": user_config.hot_post_threshold,
                    "notification_enabled": user_config.notification_enabled,
                    "created_at": user_config.created_at.isoformat(),
                    "updated_at": user_config.updated_at.isoformat()
                }
            }
        else:
            # 返回默认配置
            return {
                "success": True,
                "data": {
                    "keywords": [],
                    "collection_frequency": "hourly",
                    "data_retention_days": 30,
                    "hot_post_threshold": 100,
                    "notification_enabled": True
                }
            }
            
    except Exception as e:
        logger.error(f"获取关键词配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取关键词配置失败: {str(e)}")

@router.put("/schedule")
async def update_schedule(
    config: ScheduleConfigRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新采集计划"""
    try:
        # 验证采集频率
        valid_frequencies = ["hourly", "daily", "realtime"]
        if config.collection_frequency not in valid_frequencies:
            raise HTTPException(
                status_code=400, 
                detail=f"无效的采集频率，支持的频率: {', '.join(valid_frequencies)}"
            )
        
        # 查找或创建用户配置
        result = await db.execute(
            select(UserConfig).where(UserConfig.user_id == "default")
        )
        user_config = result.scalar_one_or_none()
        
        if user_config:
            # 更新现有配置
            user_config.collection_frequency = config.collection_frequency
            user_config.data_retention_days = config.data_retention_days
            user_config.hot_post_threshold = config.hot_post_threshold
        else:
            # 创建新配置
            user_config = UserConfig(
                user_id="default",
                collection_frequency=config.collection_frequency,
                data_retention_days=config.data_retention_days,
                hot_post_threshold=config.hot_post_threshold
            )
            db.add(user_config)
        
        await db.commit()
        await db.refresh(user_config)
        
        return {
            "success": True,
            "message": "采集计划已更新",
            "data": {
                "collection_frequency": user_config.collection_frequency,
                "data_retention_days": user_config.data_retention_days,
                "hot_post_threshold": user_config.hot_post_threshold
            }
        }
        
    except Exception as e:
        logger.error(f"更新采集计划失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新采集计划失败: {str(e)}")

@router.get("/status")
async def get_config_status(db: AsyncSession = Depends(get_db)):
    """获取配置状态"""
    try:
        result = await db.execute(
            select(UserConfig).where(UserConfig.user_id == "default")
        )
        user_config = result.scalar_one_or_none()
        
        if user_config:
            status = {
                "configured": True,
                "keywords_count": len(user_config.keywords),
                "collection_frequency": user_config.collection_frequency,
                "data_retention_days": user_config.data_retention_days,
                "hot_post_threshold": user_config.hot_post_threshold,
                "notification_enabled": user_config.notification_enabled,
                "last_updated": user_config.updated_at.isoformat()
            }
        else:
            status = {
                "configured": False,
                "keywords_count": 0,
                "collection_frequency": "hourly",
                "data_retention_days": 30,
                "hot_post_threshold": 100,
                "notification_enabled": True,
                "last_updated": None
            }
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        logger.error(f"获取配置状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取配置状态失败: {str(e)}")

@router.delete("/keywords/{keyword}")
async def remove_keyword(
    keyword: str,
    db: AsyncSession = Depends(get_db)
):
    """移除单个关键词"""
    try:
        result = await db.execute(
            select(UserConfig).where(UserConfig.user_id == "default")
        )
        user_config = result.scalar_one_or_none()
        
        if not user_config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        if keyword in user_config.keywords:
            user_config.keywords.remove(keyword)
            await db.commit()
            
            return {
                "success": True,
                "message": f"关键词 '{keyword}' 已移除",
                "data": {
                    "keywords": user_config.keywords
                }
            }
        else:
            raise HTTPException(status_code=404, detail=f"关键词 '{keyword}' 不存在")
            
    except Exception as e:
        logger.error(f"移除关键词失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"移除关键词失败: {str(e)}")

@router.post("/keywords/{keyword}")
async def add_keyword(
    keyword: str,
    db: AsyncSession = Depends(get_db)
):
    """添加单个关键词"""
    try:
        result = await db.execute(
            select(UserConfig).where(UserConfig.user_id == "default")
        )
        user_config = result.scalar_one_or_none()
        
        if user_config:
            if keyword not in user_config.keywords:
                user_config.keywords.append(keyword)
                await db.commit()
                
                return {
                    "success": True,
                    "message": f"关键词 '{keyword}' 已添加",
                    "data": {
                        "keywords": user_config.keywords
                    }
                }
            else:
                raise HTTPException(status_code=409, detail=f"关键词 '{keyword}' 已存在")
        else:
            # 创建新配置
            user_config = UserConfig(
                user_id="default",
                keywords=[keyword]
            )
            db.add(user_config)
            await db.commit()
            
            return {
                "success": True,
                "message": f"关键词 '{keyword}' 已添加",
                "data": {
                    "keywords": [keyword]
                }
            }
            
    except Exception as e:
        logger.error(f"添加关键词失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加关键词失败: {str(e)}")