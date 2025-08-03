from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal, UserConfig
from services.scraper_service import scraper_service
from services.analysis_service import analysis_service
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

# 全局调度器
scheduler = AsyncIOScheduler()

async def start_scheduler():
    """启动调度器"""
    try:
        # 添加定时任务
        
        # 每小时执行一次关键词声量监测
        scheduler.add_job(
            keyword_monitoring_task,
            CronTrigger(minute=0),  # 每小时的0分执行
            id="keyword_monitoring",
            name="关键词声量监测",
            replace_existing=True
        )
        
        # 每2小时执行一次热帖数据采集
        scheduler.add_job(
            hot_posts_collection_task,
            CronTrigger(minute=0, hour="*/2"),  # 每2小时执行
            id="hot_posts_collection",
            name="热帖数据采集",
            replace_existing=True
        )
        
        # 每6小时执行一次词云数据更新
        scheduler.add_job(
            word_cloud_update_task,
            CronTrigger(minute=0, hour="*/6"),  # 每6小时执行
            id="word_cloud_update",
            name="词云数据更新",
            replace_existing=True
        )
        
        # 每天凌晨3点执行数据清理
        scheduler.add_job(
            data_cleanup_task,
            CronTrigger(hour=3, minute=0),  # 每天凌晨3点执行
            id="data_cleanup",
            name="数据清理任务",
            replace_existing=True
        )
        
        # 启动调度器
        scheduler.start()
        logger.info("调度器已启动，定时任务已配置")
        
    except Exception as e:
        logger.error(f"启动调度器失败: {str(e)}")

async def keyword_monitoring_task():
    """关键词声量监测任务"""
    try:
        logger.info("开始执行关键词声量监测任务")
        
        async with AsyncSessionLocal() as db:
            # 获取配置的关键词
            result = await db.execute(
                select(UserConfig).where(UserConfig.user_id == "default")
            )
            user_config = result.scalar_one_or_none()
            
            if not user_config or not user_config.keywords:
                logger.warning("未配置关键词，跳过监测任务")
                return
            
            # 只有在配置为hourly或realtime时才执行
            if user_config.collection_frequency not in ["hourly", "realtime"]:
                logger.info(f"当前配置频率为 {user_config.collection_frequency}，跳过小时监测")
                return
            
            # 执行采集
            results = await scraper_service.batch_collect_data(user_config.keywords, db)
            logger.info(f"关键词监测任务完成: {results}")
            
    except Exception as e:
        logger.error(f"关键词监测任务失败: {str(e)}")

async def hot_posts_collection_task():
    """热帖数据采集任务"""
    try:
        logger.info("开始执行热帖数据采集任务")
        
        async with AsyncSessionLocal() as db:
            # 获取配置的关键词
            result = await db.execute(
                select(UserConfig).where(UserConfig.user_id == "default")
            )
            user_config = result.scalar_one_or_none()
            
            if not user_config or not user_config.keywords:
                logger.warning("未配置关键词，跳过热帖采集任务")
                return
            
            # 执行热帖采集（更详细的采集）
            for keyword in user_config.keywords:
                try:
                    posts = await scraper_service.search_notes(keyword, limit=50)
                    logger.info(f"关键词 {keyword} 采集到 {len(posts)} 条热帖")
                except Exception as e:
                    logger.error(f"采集关键词 {keyword} 的热帖失败: {str(e)}")
            
    except Exception as e:
        logger.error(f"热帖采集任务失败: {str(e)}")

async def word_cloud_update_task():
    """词云数据更新任务"""
    try:
        logger.info("开始执行词云数据更新任务")
        
        async with AsyncSessionLocal() as db:
            # 获取配置的关键词
            result = await db.execute(
                select(UserConfig).where(UserConfig.user_id == "default")
            )
            user_config = result.scalar_one_or_none()
            
            if not user_config or not user_config.keywords:
                logger.warning("未配置关键词，跳过词云更新任务")
                return
            
            # 为每个关键词更新词云和情绪分析
            for keyword in user_config.keywords:
                try:
                    # 更新词云数据
                    await analysis_service.update_word_cloud_data(keyword, db)
                    
                    # 更新情绪分析数据
                    await analysis_service.update_sentiment_analysis(keyword, db)
                    
                    logger.info(f"关键词 {keyword} 的词云和情绪分析数据已更新")
                    
                except Exception as e:
                    logger.error(f"更新关键词 {keyword} 的分析数据失败: {str(e)}")
            
    except Exception as e:
        logger.error(f"词云更新任务失败: {str(e)}")

async def data_cleanup_task():
    """数据清理任务"""
    try:
        logger.info("开始执行数据清理任务")
        
        async with AsyncSessionLocal() as db:
            # 获取数据保留配置
            result = await db.execute(
                select(UserConfig).where(UserConfig.user_id == "default")
            )
            user_config = result.scalar_one_or_none()
            
            retention_days = 30  # 默认保留30天
            if user_config and user_config.data_retention_days:
                retention_days = user_config.data_retention_days
            
            from datetime import datetime, timedelta
            from core.database import KeywordTrend, HotPost, WordCloudData, SentimentAnalysis, ScrapingLog
            
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # 清理过期数据
            tables_to_clean = [
                (KeywordTrend, KeywordTrend.date),
                (HotPost, HotPost.collected_at),
                (WordCloudData, WordCloudData.created_at),
                (SentimentAnalysis, SentimentAnalysis.created_at),
                (ScrapingLog, ScrapingLog.started_at)
            ]
            
            total_deleted = 0
            for table, date_column in tables_to_clean:
                try:
                    from sqlalchemy import delete
                    result = await db.execute(
                        delete(table).where(date_column < cutoff_date)
                    )
                    deleted_count = result.rowcount
                    total_deleted += deleted_count
                    logger.info(f"清理 {table.__tablename__} 表: 删除 {deleted_count} 条记录")
                except Exception as e:
                    logger.error(f"清理 {table.__tablename__} 表失败: {str(e)}")
            
            await db.commit()
            logger.info(f"数据清理任务完成，总计删除 {total_deleted} 条记录")
            
    except Exception as e:
        logger.error(f"数据清理任务失败: {str(e)}")

async def stop_scheduler():
    """停止调度器"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("调度器已停止")