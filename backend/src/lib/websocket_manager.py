from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, notebook_id: str):
        await websocket.accept()
        self.active_connections[notebook_id] = websocket

    def disconnect(self, notebook_id: str):
        if notebook_id in self.active_connections:
            del self.active_connections[notebook_id]

    async def send_json(self, notebook_id: str, data: dict):
        if notebook_id in self.active_connections:
            await self.active_connections[notebook_id].send_json(data)

manager = ConnectionManager()
