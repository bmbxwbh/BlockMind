"""WebUI WebSocket 管理 — 实时推送游戏状态、事件和日志"""

import asyncio
import json
import logging
import time
from typing import Set, Optional

from fastapi import WebSocket

from src.core.event_bus import EventBus, Event

logger = logging.getLogger("blockmind.webui.websocket")


class WSLogHandler(logging.Handler):
    """将日志记录广播到所有 WebSocket 客户端"""

    def __init__(self, ws_manager: "WSManager"):
        super().__init__()
        self._ws = ws_manager

    def emit(self, record: logging.LogRecord):
        try:
            msg = {
                "type": "log",
                "data": {
                    "level": record.levelname,
                    "logger": record.name,
                    "message": self.format(record),
                    "timestamp": record.created,
                },
            }
            # 非阻塞广播（fire and forget）
            asyncio.get_running_loop().create_task(self._ws.broadcast(msg))
        except Exception as e:
            # 日志广播失败不应影响正常日志记录
            if logging.getLogger("blockmind.webui.websocket").isEnabledFor(logging.DEBUG):
                logging.getLogger("blockmind.webui.websocket").debug(f"日志广播失败: {e}")


class WSManager:
    """WebSocket 连接管理器

    管理所有 WebUI 的 WebSocket 连接，支持：
    - 广播游戏状态更新
    - 推送实时事件
    - 心跳检测 (ping/pong)
    - 实时日志流
    """

    def __init__(self, event_bus: Optional[EventBus] = None):
        self._connections: Set[WebSocket] = set()
        self._event_bus = event_bus
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._log_handler: Optional[WSLogHandler] = None

    async def connect(self, ws: WebSocket) -> None:
        """接受新连接"""
        await ws.accept()
        self._connections.add(ws)
        logger.info(f"WebSocket 新连接 (总数: {len(self._connections)})")
        # 启动心跳（首次连接时）
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

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

    # ── 心跳保活 ──

    async def _heartbeat_loop(self) -> None:
        """每 30 秒 ping 一次，检测死连接"""
        while self._connections:
            await asyncio.sleep(30)
            if not self._connections:
                break
            dead = set()
            for ws in self._connections:
                try:
                    await ws.send_json({"type": "ping", "ts": time.time()})
                except Exception:
                    dead.add(ws)
            if dead:
                self._connections -= dead
                logger.info(f"心跳清理 {len(dead)} 个死连接 (剩余: {len(self._connections)})")

    # ── 事件监听 ──

    def start_event_listener(self) -> None:
        """启动事件总线监听"""
        if self._event_bus:
            async def _broadcast_handler(event: Event):
                await self.broadcast_event(event)
            self._event_bus.subscribe("*", _broadcast_handler)
            logger.info("WebSocket 事件监听已启动")

        # 注册日志 handler
        self._setup_log_handler()

    def _setup_log_handler(self) -> None:
        """注册日志广播 handler"""
        if self._log_handler is None:
            self._log_handler = WSLogHandler(self)
            self._log_handler.setLevel(logging.INFO)
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")
            self._log_handler.setFormatter(formatter)
            logging.getLogger("blockmind").addHandler(self._log_handler)
            logger.info("WebSocket 日志流已启动")

    @property
    def connection_count(self) -> int:
        return len(self._connections)
