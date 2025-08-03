from typing import List, Dict, Any
import jieba
import jieba.analyse
from wordcloud import WordCloud
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from core.database import HotPost, WordCloudData, SentimentAnalysis, KeywordTrend
import logging
import base64
from io import BytesIO

try:
    import snownlp
    SNOWNLP_AVAILABLE = True
except ImportError:
    SNOWNLP_AVAILABLE = False
    logging.warning("snownlp not available, sentiment analysis will be disabled")

logger = logging.getLogger(__name__)

class DataAnalysisService:
    def __init__(self):
        # 初始化jieba
        jieba.initialize()
        
        # 添加自定义词典（可以根据需要扩展）
        custom_words = [
            "小红书", "种草", "拔草", "好物", "推荐", "分享",
            "美妆", "护肤", "穿搭", "美食", "旅行", "生活",
            "医美", "整形", "瘦身", "健身", "养生"
        ]
        for word in custom_words:
            jieba.add_word(word)

    async def generate_word_cloud(self, texts: List[str], keyword: str = None) -> Dict[str, Any]:
        """生成词云数据"""
        try:
            if not texts:
                return {"words": [], "image": None, "total_words": 0}
            
            # 合并所有文本
            combined_text = " ".join(texts)
            
            # 使用jieba进行分词和关键词提取
            keywords = jieba.analyse.extract_tags(
                combined_text,
                topK=100,
                withWeight=True,
                allowPOS=('n', 'nr', 'ns', 'v', 'vn', 'a', 'ad')
            )
            
            if not keywords:
                return {"words": [], "image": None, "total_words": 0}
            
            # 转换为词云数据格式
            word_data = []
            for word, weight in keywords:
                if len(word) > 1 and word not in ['小红书', '大家', '这个', '觉得', '可以', '非常', '真的']:
                    word_data.append({
                        "word": word,
                        "weight": float(weight),
                        "size": int(weight * 100)
                    })
            
            # 生成词云图片
            word_cloud_image = None
            try:
                # 创建词频字典
                word_freq = {item["word"]: item["weight"] for item in word_data}
                
                # 生成词云
                wordcloud = WordCloud(
                    width=800,
                    height=400,
                    background_color='white',
                    font_path=None,  # 可以指定中文字体路径
                    max_words=50,
                    relative_scaling=0.5,
                    colormap='viridis'
                ).generate_from_frequencies(word_freq)
                
                # 转换为base64
                img_buffer = BytesIO()
                wordcloud.to_image().save(img_buffer, format='PNG')
                img_str = base64.b64encode(img_buffer.getvalue()).decode()
                word_cloud_image = f"data:image/png;base64,{img_str}"
                
            except Exception as e:
                logger.error(f"生成词云图片时出错: {str(e)}")
            
            return {
                "words": word_data[:50],  # 返回前50个词
                "image": word_cloud_image,
                "total_words": len(word_data),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"生成词云时出错: {str(e)}")
            return {"words": [], "image": None, "total_words": 0, "error": str(e)}

    async def analyze_sentiment(self, texts: List[str]) -> Dict[str, float]:
        """分析情绪"""
        if not SNOWNLP_AVAILABLE or not texts:
            return {
                "positive": 0.5,
                "negative": 0.3,
                "neutral": 0.2,
                "total_analyzed": 0
            }
        
        try:
            sentiments = []
            for text in texts:
                if text and len(text.strip()) > 5:
                    try:
                        s = snownlp.SnowNLP(text)
                        sentiment_score = s.sentiments
                        sentiments.append(sentiment_score)
                    except Exception as e:
                        logger.warning(f"分析单条文本情绪时出错: {str(e)}")
                        continue
            
            if not sentiments:
                return {
                    "positive": 0.5,
                    "negative": 0.3,
                    "neutral": 0.2,
                    "total_analyzed": 0
                }
            
            # 计算情绪分布
            positive_count = sum(1 for s in sentiments if s > 0.6)
            negative_count = sum(1 for s in sentiments if s < 0.4)
            neutral_count = len(sentiments) - positive_count - negative_count
            
            total = len(sentiments)
            
            return {
                "positive": round(positive_count / total, 3),
                "negative": round(negative_count / total, 3),
                "neutral": round(neutral_count / total, 3),
                "total_analyzed": total,
                "average_score": round(np.mean(sentiments), 3)
            }
            
        except Exception as e:
            logger.error(f"情绪分析时出错: {str(e)}")
            return {
                "positive": 0.5,
                "negative": 0.3,
                "neutral": 0.2,
                "total_analyzed": 0,
                "error": str(e)
            }

    async def calculate_trend_data(self, keyword: str, days: int = 7, db: AsyncSession = None) -> List[Dict]:
        """计算趋势数据"""
        try:
            if not db:
                return []
            
            # 计算日期范围
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # 查询趋势数据
            result = await db.execute(
                select(
                    func.date(KeywordTrend.date).label('date'),
                    func.sum(KeywordTrend.count).label('total_count')
                )
                .where(
                    and_(
                        KeywordTrend.keyword == keyword,
                        KeywordTrend.date >= start_date,
                        KeywordTrend.date <= end_date
                    )
                )
                .group_by(func.date(KeywordTrend.date))
                .order_by(func.date(KeywordTrend.date))
            )
            
            trends = result.fetchall()
            
            # 格式化数据
            trend_data = []
            for trend in trends:
                trend_data.append({
                    "date": trend.date.strftime("%m/%d"),
                    "value": trend.total_count,
                    "keyword": keyword
                })
            
            # 如果数据不足，填充零值
            if len(trend_data) < days:
                existing_dates = {item["date"] for item in trend_data}
                for i in range(days):
                    date_obj = start_date + timedelta(days=i)
                    date_str = date_obj.strftime("%m/%d")
                    if date_str not in existing_dates:
                        trend_data.append({
                            "date": date_str,
                            "value": 0,
                            "keyword": keyword
                        })
                
                # 重新排序
                trend_data.sort(key=lambda x: datetime.strptime(f"2024/{x['date']}", "%Y/%m/%d"))
            
            return trend_data
            
        except Exception as e:
            logger.error(f"计算趋势数据时出错: {str(e)}")
            return []

    async def rank_hot_posts(self, keyword: str = None, limit: int = 10, db: AsyncSession = None) -> List[Dict]:
        """排序热帖"""
        try:
            if not db:
                return []
            
            # 构建查询
            query = select(HotPost).order_by(HotPost.hot_score.desc()).limit(limit)
            
            if keyword:
                query = query.where(HotPost.keyword == keyword)
            
            result = await db.execute(query)
            hot_posts = result.scalars().all()
            
            # 格式化数据
            ranked_posts = []
            for i, post in enumerate(hot_posts, 1):
                ranked_posts.append({
                    "rank": i,
                    "title": post.title,
                    "author": post.author,
                    "likes_count": post.likes_count,
                    "comments_count": post.comments_count,
                    "hot_score": round(post.hot_score, 2),
                    "url": post.url,
                    "keyword": post.keyword,
                    "publish_time": post.publish_time.isoformat() if post.publish_time else None,
                    "collected_at": post.collected_at.isoformat()
                })
            
            return ranked_posts
            
        except Exception as e:
            logger.error(f"排序热帖时出错: {str(e)}")
            return []

    async def update_word_cloud_data(self, keyword: str, db: AsyncSession) -> bool:
        """更新词云数据"""
        try:
            # 获取最近的帖子内容
            recent_date = datetime.utcnow() - timedelta(hours=24)
            result = await db.execute(
                select(HotPost.title, HotPost.content)
                .where(
                    and_(
                        HotPost.keyword == keyword,
                        HotPost.collected_at >= recent_date
                    )
                )
                .limit(100)
            )
            
            posts = result.fetchall()
            texts = []
            for post in posts:
                if post.title:
                    texts.append(post.title)
                if post.content:
                    texts.append(post.content)
            
            if not texts:
                return False
            
            # 生成词云数据
            word_cloud_result = await self.generate_word_cloud(texts, keyword)
            
            # 保存到数据库
            current_date = datetime.utcnow()
            for word_data in word_cloud_result.get("words", []):
                word_cloud_entry = WordCloudData(
                    keyword=keyword,
                    word=word_data["word"],
                    weight=word_data["weight"],
                    date=current_date
                )
                db.add(word_cloud_entry)
            
            await db.commit()
            return True
            
        except Exception as e:
            logger.error(f"更新词云数据时出错: {str(e)}")
            return False

    async def update_sentiment_analysis(self, keyword: str, db: AsyncSession) -> bool:
        """更新情绪分析数据"""
        try:
            # 获取最近的帖子内容
            recent_date = datetime.utcnow() - timedelta(hours=24)
            result = await db.execute(
                select(HotPost.content)
                .where(
                    and_(
                        HotPost.keyword == keyword,
                        HotPost.collected_at >= recent_date,
                        HotPost.content.isnot(None)
                    )
                )
                .limit(100)
            )
            
            posts = result.scalars().all()
            texts = [post for post in posts if post and len(post.strip()) > 10]
            
            if not texts:
                return False
            
            # 分析情绪
            sentiment_result = await self.analyze_sentiment(texts)
            
            # 保存到数据库
            sentiment_entry = SentimentAnalysis(
                keyword=keyword,
                date=datetime.utcnow(),
                positive_score=sentiment_result.get("positive", 0),
                negative_score=sentiment_result.get("negative", 0),
                neutral_score=sentiment_result.get("neutral", 0),
                total_posts=sentiment_result.get("total_analyzed", 0)
            )
            
            db.add(sentiment_entry)
            await db.commit()
            return True
            
        except Exception as e:
            logger.error(f"更新情绪分析数据时出错: {str(e)}")
            return False

# 全局实例
analysis_service = DataAnalysisService()