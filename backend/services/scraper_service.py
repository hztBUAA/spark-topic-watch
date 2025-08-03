from typing import Any, List, Dict, Optional
import asyncio
import json
import os
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import HotPost, KeywordTrend, ScrapingLog
import logging

logger = logging.getLogger(__name__)

class XiaohongshuScraperService:
    def __init__(self):
        self.browser_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../browser_data")
        self.browser_context = None
        self.main_page = None
        self.is_logged_in = False
        os.makedirs(self.browser_data_dir, exist_ok=True)

    def process_url(self, url: str) -> str:
        """处理URL，确保格式正确并保留所有参数"""
        processed_url = url.strip()
        
        if processed_url.startswith('@'):
            processed_url = processed_url[1:]
        
        if processed_url.startswith('http://'):
            processed_url = 'https://' + processed_url[7:]
        elif not processed_url.startswith('https://'):
            processed_url = 'https://' + processed_url
            
        if 'xiaohongshu.com' in processed_url and 'www.xiaohongshu.com' not in processed_url:
            processed_url = processed_url.replace('xiaohongshu.com', 'www.xiaohongshu.com')
        
        return processed_url

    async def ensure_browser(self):
        """确保浏览器已启动并登录"""
        if self.browser_context is None:
            playwright_instance = await async_playwright().start()
            
            self.browser_context = await playwright_instance.chromium.launch_persistent_context(
                user_data_dir=self.browser_data_dir,
                headless=False,
                viewport={"width": 1280, "height": 800},
                timeout=60000
            )
            
            if self.browser_context.pages:
                self.main_page = self.browser_context.pages[0]
            else:
                self.main_page = await self.browser_context.new_page()
            
            self.main_page.set_default_timeout(60000)
        
        if not self.is_logged_in:
            if self.main_page:
                await self.main_page.goto("https://www.xiaohongshu.com", timeout=60000)
                await asyncio.sleep(3)
                
                login_elements = await self.main_page.query_selector_all('text="登录"') if self.main_page else []
                if not login_elements:
                    self.is_logged_in = True
                    return True
                else:
                    return False
            else:
                return False
        
        return True

    async def login(self) -> str:
        """登录小红书账号"""
        await self.ensure_browser()
        
        if self.is_logged_in:
            return "已登录小红书账号"
        
        if not self.main_page:
            return "浏览器初始化失败，请重试"
            
        await self.main_page.goto("https://www.xiaohongshu.com", timeout=60000)
        await asyncio.sleep(3)
        
        login_elements = await self.main_page.query_selector_all('text="登录"') if self.main_page else []
        if login_elements:
            await login_elements[0].click()
            
            max_wait_time = 180
            wait_interval = 5
            waited_time = 0
            
            while waited_time < max_wait_time:
                if not self.main_page:
                    return "浏览器初始化失败，请重试"
                    
                still_login = await self.main_page.query_selector_all('text="登录"')
                if not still_login:
                    self.is_logged_in = True
                    await asyncio.sleep(2)
                    return "登录成功！"
                
                await asyncio.sleep(wait_interval)
                waited_time += wait_interval
            
            return "登录等待超时。请重试或手动登录后再使用其他功能。"
        else:
            self.is_logged_in = True
            return "已登录小红书账号"

    async def search_notes(self, keywords: str, limit: int = 5) -> List[Dict]:
        """根据关键词搜索笔记"""
        login_status = await self.ensure_browser()
        if not login_status:
            raise Exception("请先登录小红书账号")
        
        if not self.main_page:
            raise Exception("浏览器初始化失败，请重试")
            
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={keywords}"
        try:
            await self.main_page.goto(search_url, timeout=60000)
            await asyncio.sleep(5)
            
            post_cards = await self.main_page.query_selector_all('section.note-item')
            
            if not post_cards:
                post_cards = await self.main_page.query_selector_all('div[data-v-a264b01a]')
            
            posts = []
            
            for card in post_cards[:limit]:
                try:
                    link_element = await card.query_selector('a[href*="/search_result/"]') if card else None
                    if not link_element:
                        continue
                    
                    href = await link_element.get_attribute('href')
                    if href and '/search_result/' in href:
                        if href.startswith('/'):
                            full_url = f"https://www.xiaohongshu.com{href}"
                        else:
                            full_url = href
                        
                        # 获取标题
                        title = "未知标题"
                        title_element = await card.query_selector('div.footer a.title span') if card else None
                        if title_element:
                            title_text = await title_element.text_content()
                            if title_text:
                                title = title_text.strip()
                        
                        posts.append({
                            "url": full_url,
                            "title": title,
                            "keyword": keywords
                        })
                        
                except Exception as e:
                    logger.error(f"处理帖子卡片时出错: {str(e)}")
                    continue
            
            return posts
            
        except Exception as e:
            logger.error(f"搜索笔记时出错: {str(e)}")
            raise

    async def get_note_content(self, url: str) -> Dict:
        """获取笔记内容"""
        login_status = await self.ensure_browser()
        if not login_status:
            raise Exception("请先登录小红书账号")
        
        if not self.main_page:
            raise Exception("浏览器初始化失败，请重试")
            
        try:
            processed_url = self.process_url(url)
            await self.main_page.goto(processed_url, timeout=60000)
            await asyncio.sleep(10)
            
            # 检查是否加载了错误页面
            error_page = await self.main_page.evaluate('''
                () => {
                    const errorTexts = [
                        "当前笔记暂时无法浏览",
                        "内容不存在",
                        "页面不存在",
                        "内容已被删除"
                    ];
                    
                    for (const text of errorTexts) {
                        if (document.body.innerText.includes(text)) {
                            return {
                                isError: true,
                                errorText: text
                            };
                        }
                    }
                    
                    return { isError: false };
                }
            ''')
            
            if error_page.get("isError", False):
                raise Exception(f"无法获取笔记内容: {error_page.get('errorText', '未知错误')}")
            
            post_content = {}
            
            # 获取标题
            title_element = await self.main_page.query_selector('#detail-title')
            if title_element:
                title = await title_element.text_content()
                post_content["title"] = title.strip() if title else "未知标题"
            else:
                post_content["title"] = "未知标题"
            
            # 获取作者
            author_element = await self.main_page.query_selector('span.username')
            if author_element:
                author = await author_element.text_content()
                post_content["author"] = author.strip() if author else "未知作者"
            else:
                post_content["author"] = "未知作者"
            
            # 获取内容
            content_element = await self.main_page.query_selector('#detail-desc .note-text')
            if content_element:
                content_text = await content_element.text_content()
                post_content["content"] = content_text.strip() if content_text else "未能获取内容"
            else:
                post_content["content"] = "未能获取内容"
            
            # 获取互动数据
            post_content["likes_count"] = await self._extract_interaction_count("点赞")
            post_content["comments_count"] = await self._extract_interaction_count("评论")
            
            return post_content
            
        except Exception as e:
            logger.error(f"获取笔记内容时出错: {str(e)}")
            raise

    async def _extract_interaction_count(self, interaction_type: str) -> int:
        """提取互动数量"""
        try:
            if not self.main_page:
                return 0
                
            # 这里需要根据实际页面结构来获取点赞和评论数
            # 由于小红书页面结构可能变化，这里提供一个基础实现
            count_text = await self.main_page.evaluate(f'''
                () => {{
                    const elements = Array.from(document.querySelectorAll('*'));
                    for (const el of elements) {{
                        if (el.textContent && el.textContent.includes('{interaction_type}')) {{
                            const match = el.textContent.match(/(\d+)/);
                            if (match) {{
                                return parseInt(match[1], 10);
                            }}
                        }}
                    }}
                    return 0;
                }}
            ''')
            return count_text or 0
        except Exception:
            return 0

    def calculate_hot_score(self, likes: int, comments: int) -> float:
        """计算热度分数"""
        return likes * 0.7 + comments * 0.3

    async def batch_collect_data(self, keywords: List[str], db: AsyncSession) -> Dict:
        """批量采集数据"""
        results = {
            "success_count": 0,
            "error_count": 0,
            "total_posts": 0,
            "keywords_processed": []
        }
        
        for keyword in keywords:
            try:
                # 记录开始采集
                log = ScrapingLog(
                    task_type="search",
                    keyword=keyword,
                    status="running",
                    message=f"开始采集关键词: {keyword}"
                )
                db.add(log)
                await db.commit()
                
                # 搜索笔记
                posts = await self.search_notes(keyword, limit=20)
                
                # 记录趋势数据
                trend = KeywordTrend(
                    keyword=keyword,
                    date=datetime.utcnow(),
                    count=len(posts)
                )
                db.add(trend)
                
                # 处理每个帖子
                for post_data in posts:
                    try:
                        # 获取详细内容
                        content = await self.get_note_content(post_data["url"])
                        
                        # 计算热度分数
                        hot_score = self.calculate_hot_score(
                            content.get("likes_count", 0),
                            content.get("comments_count", 0)
                        )
                        
                        # 保存热帖数据
                        hot_post = HotPost(
                            post_id=post_data["url"].split("/")[-1],
                            title=content.get("title", ""),
                            author=content.get("author", ""),
                            content=content.get("content", ""),
                            url=post_data["url"],
                            likes_count=content.get("likes_count", 0),
                            comments_count=content.get("comments_count", 0),
                            hot_score=hot_score,
                            keyword=keyword,
                            publish_time=datetime.utcnow()
                        )
                        
                        # 检查是否已存在
                        existing = await db.execute(
                            select(HotPost).where(HotPost.post_id == hot_post.post_id)
                        )
                        if not existing.scalar_one_or_none():
                            db.add(hot_post)
                        
                        results["total_posts"] += 1
                        
                    except Exception as e:
                        logger.error(f"处理帖子时出错: {str(e)}")
                        results["error_count"] += 1
                
                results["success_count"] += 1
                results["keywords_processed"].append(keyword)
                
                # 更新日志
                log.status = "success"
                log.data_count = len(posts)
                log.completed_at = datetime.utcnow()
                log.message = f"成功采集 {len(posts)} 条数据"
                
                await db.commit()
                
            except Exception as e:
                logger.error(f"采集关键词 {keyword} 时出错: {str(e)}")
                results["error_count"] += 1
                
                # 更新日志
                if 'log' in locals():
                    log.status = "failed"
                    log.completed_at = datetime.utcnow()
                    log.message = f"采集失败: {str(e)}"
                    await db.commit()
        
        return results

# 全局实例
scraper_service = XiaohongshuScraperService()