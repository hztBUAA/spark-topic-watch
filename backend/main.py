from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from api.routes import config, scraper, monitor, data
from core.database import init_db
from core.scheduler import start_scheduler
from services.websocket_manager import ConnectionManager

# WebSocket connection manager
manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await start_scheduler()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="小红书舆情监测系统 API",
    description="Xiaohongshu Social Media Monitoring System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(config.router, prefix="/api/config", tags=["配置管理"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["数据采集"])
app.include_router(monitor.router, prefix="/api/monitor", tags=["实时监测"])
app.include_router(data.router, prefix="/api/data", tags=["数据查询"])

@app.websocket("/ws/monitor/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Message: {data}", client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)

@app.get("/")
async def root():
    return {"message": "小红书舆情监测系统 API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )