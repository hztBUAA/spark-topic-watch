# 小红书舆情监测系统 - 后端API

## 项目简介

基于FastAPI开发的小红书舆情监测系统后端，提供实时数据采集、关键词趋势分析、热帖排行榜、词云生成和情绪分析等功能。

## 功能特性

- 🔍 **关键词监测**: 支持多关键词实时监测
- 📈 **趋势分析**: 关键词声量趋势数据可视化
- 🔥 **热帖排行**: 基于热度算法的帖子排序
- ☁️ **词云生成**: 智能热词提取和词云可视化
- 😊 **情绪分析**: 基于机器学习的情绪倾向分析
- ⚡ **实时监测**: WebSocket实时数据推送
- 📊 **数据管理**: 完整的数据采集和存储方案

## 技术栈

- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL + SQLAlchemy
- **缓存**: Redis
- **任务队列**: Celery + APScheduler
- **数据采集**: Playwright + BeautifulSoup
- **数据分析**: pandas + jieba + wordcloud + snownlp
- **部署**: Docker + Docker Compose

## 快速开始

### 环境要求

- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose (推荐)

### 使用Docker部署 (推荐)

1. 克隆项目
```bash
git clone <repository-url>
cd backend
```

2. 启动服务
```bash
docker-compose up -d
```

3. 查看服务状态
```bash
docker-compose ps
```

4. 访问API文档
```
http://localhost:8000/docs
```

### 本地开发部署

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 安装Playwright浏览器
```bash
playwright install chromium
```

3. 配置环境变量
```bash
export DATABASE_URL="sqlite+aiosqlite:///./xiaohongshu_monitor.db"
export REDIS_URL="redis://localhost:6379/0"
```

4. 启动应用
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API接口文档

### 配置管理

- `POST /api/config/keywords` - 设置监测关键词
- `GET /api/config/keywords` - 获取关键词配置
- `PUT /api/config/schedule` - 更新采集计划
- `GET /api/config/status` - 获取配置状态

### 数据查询

- `GET /api/data/trends/{keyword}` - 获取关键词趋势
- `GET /api/data/hot-posts` - 获取热帖排行榜
- `GET /api/data/word-cloud` - 获取词云数据
- `GET /api/data/sentiment/{keyword}` - 获取情绪分析
- `GET /api/data/stats` - 获取统计数据

### 数据采集

- `POST /api/scraper/login` - 登录小红书账号
- `POST /api/scraper/search` - 手动触发搜索
- `POST /api/scraper/analyze` - 分析指定笔记
- `GET /api/scraper/logs` - 获取采集日志

### 实时监测

- `POST /api/monitor/start` - 启动实时监测
- `POST /api/monitor/stop` - 停止监测
- `GET /api/monitor/status` - 获取监测状态
- `WebSocket /ws/monitor/{client_id}` - 实时数据推送

## 配置说明

### 数据库配置

```python
# SQLite (开发环境)
DATABASE_URL = "sqlite+aiosqlite:///./xiaohongshu_monitor.db"

# PostgreSQL (生产环境)
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"
```

### 采集频率配置

- `realtime`: 实时监测 (5分钟间隔)
- `hourly`: 每小时采集
- `daily`: 每日采集

### 热度计算公式

```python
hot_score = likes_count * 0.7 + comments_count * 0.3
```

## 定时任务

系统包含以下定时任务：

- **关键词监测**: 每小时执行，采集关键词数据
- **热帖采集**: 每2小时执行，收集热门帖子
- **数据分析**: 每6小时执行，更新词云和情绪分析
- **数据清理**: 每天凌晨执行，清理过期数据

## 监控和日志

### 应用日志

```bash
# 查看应用日志
docker-compose logs -f api

# 查看Celery日志
docker-compose logs -f worker
```

### 健康检查

```bash
curl http://localhost:8000/health
```

## 开发指南

### 项目结构

```
backend/
├── main.py                 # FastAPI应用入口
├── core/
│   ├── database.py         # 数据库配置和模型
│   └── scheduler.py        # 任务调度器
├── api/
│   └── routes/            # API路由
│       ├── config.py      # 配置管理
│       ├── data.py        # 数据查询
│       ├── scraper.py     # 数据采集
│       └── monitor.py     # 实时监测
├── services/
│   ├── scraper_service.py  # 数据采集服务
│   ├── analysis_service.py # 数据分析服务
│   └── websocket_manager.py # WebSocket管理
├── requirements.txt        # Python依赖
├── Dockerfile             # Docker构建文件
└── docker-compose.yml     # Docker编排文件
```

### 添加新功能

1. 在`services/`目录下创建服务类
2. 在`api/routes/`目录下添加API路由
3. 在`core/database.py`中添加数据模型（如需要）
4. 更新`main.py`注册新路由

### 数据库迁移

```bash
# 生成迁移文件
alembic revision --autogenerate -m "Add new table"

# 执行迁移
alembic upgrade head
```

## 部署指南

### 生产环境部署

1. 修改`docker-compose.yml`中的密码
2. 配置反向代理 (Nginx)
3. 启用HTTPS
4. 配置监控和日志收集

### 性能优化

- 使用PostgreSQL连接池
- 配置Redis缓存策略
- 调整Celery worker数量
- 优化数据库索引

## 故障排除

### 常见问题

1. **浏览器启动失败**
   - 检查Docker容器权限
   - 确认Playwright依赖完整安装

2. **数据库连接失败**
   - 检查数据库服务状态
   - 验证连接字符串配置

3. **WebSocket连接断开**
   - 检查网络配置
   - 增加连接重试机制

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs api
docker-compose logs worker
```

## 安全说明

- 仅采集公开数据，遵守robots.txt
- 实现请求频率限制，避免过度访问
- 不保存用户隐私信息
- 支持数据自动清理策略

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。