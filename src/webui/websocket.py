"""WebUI WebSocket 管理 — 实时推送游戏状态和事件"""

import asyncio
import json
import logging
from typing import Set, Optional

from fastapi import WebSocket

from src.core.event_bus import EventBus, Event

logger = logging.getLogger("blockmind.webui.websocket")


class WSManager:
    """WebSocket 连接管理器

    管理所有 WebUI 的 WebSocket 连接，支持：
    - 广播游戏状态更新
    - 推送实时事件
    - 心跳检测
    """

    def __init__(self, event_bus: Optional[EventBus] = None):
        self._connections: Set[WebSocket] = set()
        self._event_bus = event_bus
        self._broadcast_task: Optional[asyncio.Task] = None

    async def connect(self, ws: WebSocket) -> None:
        """接受新连接"""
        await ws.accept()
        self._connections.add(ws)
        logger.info(f"WebSocket 新连接 (总数: {len(self._connections)})")

    def disconnect(self, ws: WebSocket) -> None:
        """移除连接"""
        self._connections.discard(ws)
        logger.info(f"WebSocket 断开 (剩余: {len(self._connections)})")

    async def broadcast(self, message: dict) -> None:
        """广播消息到所有连接"""
        if not self._connections:
            return
        data = json.dumps(message, ensure_ascii=False)
        disconnected = set()
        for ws in self._connections:
            try:
                await ws.send_text(data)
            except Exception:
                disconnected.add(ws)
        self._connections -= disconnected

    async def broadcast_event(self, event: Event) -> None:
        """广播事件"""
        await self.broadcast({
            "type": event.type,
            "data": event.data,
            "timestamp": event.timestamp.isoformat() if hasattr(event.timestamp, 'isoformat') else str(event.timestamp),
        })

    async def broadcast_status(self, status: dict) -> None:
        """广播状态更新"""
        await self.broadcast({"type": "status_update", "data": status})

    def start_event_listener(self) -> None:
        """启动事件总线监听（在事件总线上注册处理器）"""
        if self._event_bus:
            # 注册所有事件类型的广播
            async def _broadcast_handler(event: Event):
                await self.broadcast_event(event)
            self._event_bus.subscribe("*", _broadcast_handler)
            logger.info("WebSocket 事件监听已启动")

    @property
    def connection_count(self) -> int:
        return len(self._connections)
