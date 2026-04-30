"""Mod WebSocket 客户端 — 接收 Mod 推送的实时游戏事件

Features:
- Automatic reconnection with exponential backoff
- Configurable backoff parameters
- Backoff reset on successful connection
- Connection attempt tracking
"""

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

    Supports automatic reconnection with exponential backoff:
    - Initial delay starts at `initial_backoff` seconds
    - Each consecutive failure multiplies the delay by `backoff_multiplier`
    - Delay is capped at `max_backoff` seconds
    - Backoff resets to initial on any successful connection
    """

    def __init__(
        self,
        host: str,
        port: int,
        event_bus: EventBus,
        reconnect_interval: float = 5.0,
        initial_backoff: float = 2.0,
        max_backoff: float = 120.0,
        backoff_multiplier: float = 2.0,
    ):
        self.url = f"ws://{host}:{port}/ws/events"
        self.event_bus = event_bus
        # Keep legacy param for backwards compat but prefer backoff params
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
        self.backoff_multiplier = backoff_multiplier
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._listen_task: Optional[asyncio.Task] = None
        self._running = False
        self._current_backoff: float = 0.0
        self._reconnect_attempts: int = 0
        self._total_reconnects: int = 0
        logger.info(f"ModWebSocketClient 初始化: {self.url}")

    async def connect(self) -> None:
        """建立 WebSocket 连接并开始监听"""
        if self._running:
            return
        self._running = True
        self._current_backoff = 0.0  # Will be set to initial on first retry
        self._reconnect_attempts = 0
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

    @property
    def reconnect_attempts(self) -> int:
        """Current consecutive reconnect attempt count."""
        return self._reconnect_attempts

    @property
    def total_reconnects(self) -> int:
        """Total number of reconnections since start."""
        return self._total_reconnects

    def _next_backoff(self) -> float:
        """Calculate the next backoff delay using exponential strategy.

        Returns the delay in seconds, capped at max_backoff.
        """
        if self._current_backoff <= 0:
            self._current_backoff = self.initial_backoff
        else:
            self._current_backoff = min(
                self._current_backoff * self.backoff_multiplier,
                self.max_backoff,
            )
        return self._current_backoff

    def _reset_backoff(self) -> None:
        """Reset backoff state after a successful connection."""
        self._current_backoff = 0.0
        self._reconnect_attempts = 0

    async def _listen_loop(self) -> None:
        """持续监听 WebSocket 消息，支持自动重连（指数退避）"""
        while self._running:
            try:
                await self._connect_ws()
                # Connection succeeded — reset backoff
                self._reset_backoff()
                await self._receive_messages()
            except aiohttp.WSServerHandshakeError as e:
                if e.status == 404:
                    # Mod 没有 WebSocket，停止重连
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"WebSocket 异常: {e}")

            if self._running:
                delay = self._next_backoff()
                self._reconnect_attempts += 1
                self._total_reconnects += 1
                logger.info(
                    f"将在 {delay:.1f}s 后重连 "
                    f"(第 {self._reconnect_attempts} 次连续重试，"
                    f"累计 {self._total_reconnects} 次重连)..."
                )
                await asyncio.sleep(delay)

    async def _connect_ws(self) -> None:
        """建立 WebSocket 连接"""
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = aiohttp.ClientSession()
        try:
            self._ws = await self._session.ws_connect(self.url)
            logger.info("WebSocket 连接成功")
        except aiohttp.WSServerHandshakeError as e:
            # 404 = Mod 没有 WebSocket 端点，降级为轮询模式
            if e.status == 404:
                logger.info("Mod 无 WebSocket 端点，事件将通过 HTTP 轮询获取")
                self._running = False  # 停止重连
            raise
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
