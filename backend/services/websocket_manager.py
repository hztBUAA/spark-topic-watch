from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connection established: {client_id}")
        
        # 发送连接确认消息
        await self.send_personal_message({
            "type": "connection_established",
            "client_id": client_id,
            "message": "WebSocket连接已建立"
        }, client_id)

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket connection closed: {client_id}")

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {str(e)}")
                # 连接可能已断开，移除它
                self.disconnect(client_id)

    async def broadcast(self, message: dict):
        """广播消息给所有连接的客户端"""
        if not self.active_connections:
            return
        
        disconnected_clients = []
        message_text = json.dumps(message, ensure_ascii=False)
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message_text)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {str(e)}")
                disconnected_clients.append(client_id)
        
        # 清理断开的连接
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    async def send_to_group(self, message: dict, group: List[str]):
        """发送消息给指定的客户端组"""
        for client_id in group:
            await self.send_personal_message(message, client_id)

    def get_connection_count(self) -> int:
        """获取当前连接数"""
        return len(self.active_connections)

    def get_connected_clients(self) -> List[str]:
        """获取所有连接的客户端ID"""
        return list(self.active_connections.keys())

# 全局连接管理器实例
manager = ConnectionManager()