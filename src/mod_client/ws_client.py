"""Mod WebSocket 客户端 — 接收 Mod 推送的实时游戏事件"""

import asyncio
import json
import logging
from typing import Optional

import aiohttp

from src.core.event_bus import EventBus, Event
from src.mod_client.models import WSMessage

logger = logging.getLogger("blockmind.ws_client")


class ModWebSocketClient:
    """Mod WebSocket 客户端

    连接 Mod 的 /ws/events 端点，接收实时游戏事件（聊天、伤害、方块变化等），
    并将事件转发到 Python 端的 EventBus。
    """

    def __init__(self, host: str, port: int, event_bus: EventBus, reconnect_interval: float = 5.0):
        self.url = f"ws://{host}:{port}/ws/events"
        self.event_bus = event_bus
        self.reconnect_interval = reconnect_interval
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._listen_task: Optional[asyncio.Task] = None
        self._running = False
        logger.info(f"ModWebSocketClient 初始化: {self.url}")

    async def connect(self) -> None:
        """建立 WebSocket 连接并开始监听"""
        if self._running:
            return
        self._running = True
        self._listen_task = asyncio.create_task(self._listen_loop())
        logger.info("WebSocket 监听任务已启动")

    async def disconnect(self) -> None:
        """断开连接并停止监听"""
        self._running = False
        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        if self._ws and not self._ws.closed:
            await self._ws.close()
        if self._session and not self._session.closed:
            await self._session.close()
        self._ws = None
        self._session = None
        logger.info("WebSocket 连接已断开")

    @property
    def is_connected(self) -> bool:
        return self._ws is not None and not self._ws.closed

    async def _listen_loop(self) -> None:
        """持续监听 WebSocket 消息，支持自动重连"""
        while self._running:
            try:
                await self._connect_ws()
                await self._receive_messages()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"WebSocket 异常: {e}")
            if self._running:
                logger.info(f"将在 {self.reconnect_interval}s 后重连...")
                await asyncio.sleep(self.reconnect_interval)

    async def _connect_ws(self) -> None:
        """建立 WebSocket 连接"""
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = aiohttp.ClientSession()
        try:
            self._ws = await self._session.ws_connect(self.url)
            logger.info("WebSocket 连接成功")
        except Exception as e:
            logger.error(f"WebSocket 连接失败: {e}")
            raise

    async def _receive_messages(self) -> None:
        """接收并处理消息"""
        async for msg in self._ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    ws_msg = WSMessage.from_dict(data)
                    event = Event(
                        type=ws_msg.type,
                        data=ws_msg.data,
                        source="mod_ws",
                    )
                    await self.event_bus.emit(event)
                    logger.debug(f"收到事件: {ws_msg.type}")
                except json.JSONDecodeError:
                    logger.warning(f"无法解析消息: {msg.data}")
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error(f"WebSocket 错误: {self._ws.exception()}")
                break
            elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING):
                logger.info("WebSocket 连接关闭")
                break
