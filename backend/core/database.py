from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON
from datetime import datetime
import os

# Database URL - can be configured via environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./xiaohongshu_monitor.db")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

class UserConfig(Base):
    __tablename__ = "user_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, default="default")
    keywords = Column(JSON, default=list)  # 监测关键词列表
    collection_frequency = Column(String(20), default="hourly")  # hourly, daily, realtime
    data_retention_days = Column(Integer, default=30)
    hot_post_threshold = Column(Integer, default=100)  # 热帖阈值
    notification_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class KeywordTrend(Base):
    __tablename__ = "keyword_trends"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(100), index=True)
    date = Column(DateTime, index=True)
    count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class HotPost(Base):
    __tablename__ = "hot_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String(100), unique=True, index=True)
    title = Column(Text)
    author = Column(String(100))
    content = Column(Text)
    url = Column(Text)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    hot_score = Column(Float, default=0.0)  # 热度分数
    keyword = Column(String(100), index=True)
    publish_time = Column(DateTime)
    collected_at = Column(DateTime, default=datetime.utcnow)

class WordCloudData(Base):
    __tablename__ = "word_cloud_data"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(100), index=True)
    word = Column(String(50))
    weight = Column(Float)
    date = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(100), index=True)
    date = Column(DateTime, index=True)
    positive_score = Column(Float, default=0.0)
    negative_score = Column(Float, default=0.0)
    neutral_score = Column(Float, default=0.0)
    total_posts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class ScrapingLog(Base):
    __tablename__ = "scraping_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(50))  # search, analyze, comment
    keyword = Column(String(100))
    status = Column(String(20))  # success, failed, running
    message = Column(Text)
    data_count = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)