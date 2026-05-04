from typing import Dict, List
from fastapi import WebSocket
import json
from schemas.ws import JobUpdate


class WebSocketManager:
    """WebSocket 연결을 job_id별로 관리하고 메시지를 브로드캐스트"""

    def __init__(self):
        # job_id -> [WebSocket, WebSocket, ...]
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        """WebSocket 연결 등록"""
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)

    def disconnect(self, job_id: str, websocket: WebSocket):
        """WebSocket 연결 해제"""
        if job_id in self.active_connections:
            self.active_connections[job_id].remove(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

    async def broadcast(self, job_id: str, payload: JobUpdate):
        """해당 job_id의 모든 WebSocket 클라이언트에게 메시지 브로드캐스트"""
        if job_id not in self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections[job_id]:
            try:
                await connection.send_json(json.loads(payload.model_dump_json()))
            except Exception:
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(job_id, connection)


websocket_manager = WebSocketManager()
