from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import datetime, timedelta
from core.database import get_db, KeywordTrend, HotPost, WordCloudData, SentimentAnalysis
from services.analysis_service import analysis_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/trends/{keyword}")
async def get_keyword_trends(
    keyword: str,
    days: int = Query(7, ge=1, le=30, description="天数范围"),
    db: AsyncSession = Depends(get_db)
):
    """获取关键词趋势数据"""
    try:
        trend_data = await analysis_service.calculate_trend_data(keyword, days, db)
        
        return {
            "success": True,
            "data": trend_data,
            "keyword": keyword,
            "days": days,
            "total_points": len(trend_data)
        }
    except Exception as e:
        logger.error(f"获取趋势数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")

@router.get("/hot-posts")
async def get_hot_posts(
    keyword: Optional[str] = Query(None, description="关键词筛选"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取热帖排行榜"""
    try:
        hot_posts = await analysis_service.rank_hot_posts(keyword, limit, db)
        
        return {
            "success": True,
            "data": hot_posts,
            "keyword": keyword,
            "total": len(hot_posts)
        }
    except Exception as e:
        logger.error(f"获取热帖数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热帖数据失败: {str(e)}")

@router.get("/word-cloud")
async def get_word_cloud(
    keyword: Optional[str] = Query(None, description="关键词筛选"),
    hours: int = Query(24, ge=1, le=168, description="时间范围（小时）"),
    db: AsyncSession = Depends(get_db)
):
    """获取词云数据"""
    try:
        # 计算时间范围
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        if keyword:
            # 查询特定关键词的词云数据
            result = await db.execute(
                select(WordCloudData.word, WordCloudData.weight)
                .where(
                    and_(
                        WordCloudData.keyword == keyword,
                        WordCloudData.date >= start_time
                    )
                )
                .order_by(WordCloudData.weight.desc())
                .limit(50)
            )
            word_data = result.fetchall()
            
            words = [
                {
                    "word": word.word,
                    "weight": float(word.weight),
                    "size": int(word.weight * 100)
                }
                for word in word_data
            ]
        else:
            # 如果没有指定关键词，获取所有关键词的词云数据
            result = await db.execute(
                select(
                    WordCloudData.word,
                    func.avg(WordCloudData.weight).label('avg_weight')
                )
                .where(WordCloudData.date >= start_time)
                .group_by(WordCloudData.word)
                .order_by(func.avg(WordCloudData.weight).desc())
                .limit(50)
            )
            word_data = result.fetchall()
            
            words = [
                {
                    "word": word.word,
                    "weight": float(word.avg_weight),
                    "size": int(word.avg_weight * 100)
                }
                for word in word_data
            ]
        
        return {
            "success": True,
            "data": {
                "words": words,
                "total_words": len(words),
                "keyword": keyword,
                "hours": hours,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"获取词云数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取词云数据失败: {str(e)}")

@router.get("/sentiment/{keyword}")
async def get_sentiment_analysis(
    keyword: str,
    days: int = Query(7, ge=1, le=30, description="天数范围"),
    db: AsyncSession = Depends(get_db)
):
    """获取情绪分析数据"""
    try:
        # 计算时间范围
        start_time = datetime.utcnow() - timedelta(days=days)
        
        # 查询情绪分析数据
        result = await db.execute(
            select(SentimentAnalysis)
            .where(
                and_(
                    SentimentAnalysis.keyword == keyword,
                    SentimentAnalysis.date >= start_time
                )
            )
            .order_by(SentimentAnalysis.date.desc())
        )
        
        sentiment_data = result.scalars().all()
        
        if not sentiment_data:
            # 如果没有历史数据，尝试实时分析
            await analysis_service.update_sentiment_analysis(keyword, db)
            
            # 重新查询
            result = await db.execute(
                select(SentimentAnalysis)
                .where(
                    and_(
                        SentimentAnalysis.keyword == keyword,
                        SentimentAnalysis.date >= start_time
                    )
                )
                .order_by(SentimentAnalysis.date.desc())
            )
            sentiment_data = result.scalars().all()
        
        # 格式化数据
        sentiment_trends = []
        total_positive = 0
        total_negative = 0
        total_neutral = 0
        total_posts = 0
        
        for data in sentiment_data:
            sentiment_trends.append({
                "date": data.date.strftime("%m/%d"),
                "positive": data.positive_score,
                "negative": data.negative_score,
                "neutral": data.neutral_score,
                "total_posts": data.total_posts
            })
            
            total_positive += data.positive_score * data.total_posts
            total_negative += data.negative_score * data.total_posts
            total_neutral += data.neutral_score * data.total_posts
            total_posts += data.total_posts
        
        # 计算总体情绪
        overall_sentiment = {
            "positive": round(total_positive / total_posts, 3) if total_posts > 0 else 0,
            "negative": round(total_negative / total_posts, 3) if total_posts > 0 else 0,
            "neutral": round(total_neutral / total_posts, 3) if total_posts > 0 else 0
        }
        
        return {
            "success": True,
            "data": {
                "trends": sentiment_trends,
                "overall": overall_sentiment,
                "total_analyzed": total_posts,
                "keyword": keyword,
                "days": days
            }
        }
        
    except Exception as e:
        logger.error(f"获取情绪分析数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取情绪分析数据失败: {str(e)}")

@router.get("/stats")
async def get_stats(
    keyword: Optional[str] = Query(None, description="关键词筛选"),
    db: AsyncSession = Depends(get_db)
):
    """获取统计数据"""
    try:
        stats = {}
        
        if keyword:
            # 特定关键词的统计
            # 监测关键词数
            stats["monitored_keywords"] = 1
            
            # 热帖数量
            hot_posts_result = await db.execute(
                select(func.count(HotPost.id))
                .where(HotPost.keyword == keyword)
            )
            stats["hot_posts"] = hot_posts_result.scalar() or 0
            
            # 总互动数
            interactions_result = await db.execute(
                select(
                    func.sum(HotPost.likes_count + HotPost.comments_count)
                )
                .where(HotPost.keyword == keyword)
            )
            stats["total_interactions"] = interactions_result.scalar() or 0
            
            # 情绪指数
            recent_sentiment = await db.execute(
                select(SentimentAnalysis)
                .where(SentimentAnalysis.keyword == keyword)
                .order_by(SentimentAnalysis.date.desc())
                .limit(1)
            )
            sentiment = recent_sentiment.scalar_one_or_none()
            if sentiment:
                stats["sentiment_index"] = round(sentiment.positive_score * 100, 1)
            else:
                stats["sentiment_index"] = 50.0
            
        else:
            # 全局统计
            # 监测关键词数
            keywords_result = await db.execute(
                select(func.count(func.distinct(HotPost.keyword)))
            )
            stats["monitored_keywords"] = keywords_result.scalar() or 0
            
            # 热帖数量
            hot_posts_result = await db.execute(
                select(func.count(HotPost.id))
            )
            stats["hot_posts"] = hot_posts_result.scalar() or 0
            
            # 总互动数
            interactions_result = await db.execute(
                select(
                    func.sum(HotPost.likes_count + HotPost.comments_count)
                )
            )
            stats["total_interactions"] = interactions_result.scalar() or 0
            
            # 平均情绪指数
            avg_sentiment_result = await db.execute(
                select(func.avg(SentimentAnalysis.positive_score))
            )
            avg_sentiment = avg_sentiment_result.scalar()
            stats["sentiment_index"] = round(avg_sentiment * 100, 1) if avg_sentiment else 50.0
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"获取统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")