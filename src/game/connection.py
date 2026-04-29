"""MC 服务器连接管理器

负责与 Minecraft 服务器建立和维护连接。
支持正版/离线模式，断线自动重连（指数退避）。
"""
import asyncio
import logging
import time
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from src.config.loader import GameConfig
from src.core.event_bus import EventBus, Event


class ConnectionState(Enum):
    """连接状态枚举"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"


@dataclass
class ConnectionInfo:
    """连接信息"""
    server_ip: str
    server_port: int
    username: str
    version: str
    state: ConnectionState = ConnectionState.DISCONNECTED
    connected_at: float = 0.0
    last_heartbeat: float = 0.0
    reconnect_count: int = 0


class MCConnection:
    """
    Minecraft 服务器连接管理器

    功能：
    1. 连接到 MC 服务器（支持正版/离线模式）
    2. 断线指数退避重连（5s → 10s → 20s → ... → 60s 上限）
    3. 心跳检测
    4. 状态同步
    5. 发送聊天消息
    6. 执行游戏动作
    """

    def __init__(self, config: GameConfig, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger("blockmind.connection")

        self._state = ConnectionState.DISCONNECTED
        self._client = None  # pyCraft client 实例（P1 后续接入）
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._reconnect_task: Optional[asyncio.Task] = None
        self._retry_count = 0
        self._max_retry_delay = 60  # 最大重连间隔（秒）
        self._base_delay = config.reconnect.interval  # 基础重连间隔
        self._connected_at: float = 0.0
        self._last_heartbeat: float = 0.0

        # 回调函数
        self._on_chat_message: Optional[Callable] = None
        self._on_state_change: Optional[Callable] = None

        self.logger.info(f"MCConnection 初始化: {config.server_ip}:{config.server_port}")

    # ─── 连接管理 ───────────────────────────────────────────

    async def connect(self) -> bool:
        """
        连接到 MC 服务器

        Returns:
            bool: 连接是否成功
        """
        if self._state == ConnectionState.CONNECTED:
            self.logger.warning("已连接，忽略重复连接请求")
            return True

        self._state = ConnectionState.CONNECTING
        await self.event_bus.emit(Event(
            type="connection.connecting",
            data={"server": f"{self.config.server_ip}:{self.config.server_port}"},
            source="connection"
        ))

        try:
            self.logger.info(f"正在连接 {self.config.server_ip}:{self.config.server_port}...")

            # TODO: P1 后续接入 pyCraft 连接逻辑
            # 1. 根据 auth_mode 选择连接方式
            # 2. 处理连接异常
            # 3. 启动心跳检测

            # 桩代码：模拟连接成功
            await asyncio.sleep(0.1)

            self._state = ConnectionState.CONNECTED
            self._connected_at = time.time()
            self._last_heartbeat = time.time()
            self._retry_count = 0

            # 启动心跳检测
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            self.logger.info("✅ 连接成功")
            await self.event_bus.emit(Event(
                type="connection.established",
                data={"server": f"{self.config.server_ip}:{self.config.server_port}"},
                source="connection"
            ))

            return True

        except Exception as e:
            self.logger.error(f"❌ 连接失败: {e}")
            self._state = ConnectionState.DISCONNECTED
            await self.event_bus.emit(Event(
                type="connection.failed",
                data={"error": str(e)},
                source="connection"
            ))

            # 如果启用自动重连，尝试重连
            if self.config.reconnect.enabled:
                self._reconnect_task = asyncio.create_task(self._reconnect_loop())

            return False

    async def disconnect(self) -> None:
        """断开连接"""
        self.logger.info("断开连接...")

        # 停止心跳
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        # 停止重连
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass

        # TODO: 关闭 pyCraft 客户端
        self._client = None

        self._state = ConnectionState.DISCONNECTED
        self._connected_at = 0.0

        self.logger.info("✅ 已断开连接")
        await self.event_bus.emit(Event(
            type="connection.lost",
            data={"reason": "manual_disconnect"},
            source="connection"
        ))

    async def reconnect(self) -> bool:
        """手动重连"""
        self.logger.info("手动重连...")
        await self.disconnect()
        return await self.connect()

    # ─── 聊天与动作 ─────────────────────────────────────────

    async def send_chat(self, message: str) -> None:
        """
        发送聊天消息

        Args:
            message: 要发送的消息
        """
        if self._state != ConnectionState.CONNECTED:
            self.logger.warning(f"未连接，无法发送消息: {message}")
            return

        self.logger.info(f"[CHAT] 发送: {message}")

        # TODO: 调用 pyCraft 发送聊天消息
        # self._client.send_chat(message)

        await self.event_bus.emit(Event(
            type="chat.sent",
            data={"message": message},
            source="connection"
        ))

    async def get_world_state(self) -> Dict[str, Any]:
        """
        获取当前世界状态快照

        Returns:
            dict: 包含世界信息的字典
        """
        # TODO: 从 pyCraft 获取世界状态
        return {
            "dimension": "overworld",
            "time_of_day": 0,
            "weather": "clear",
            "difficulty": "normal",
            "day_count": 1,
        }

    async def get_entity_state(self, entity_id: int) -> Dict[str, Any]:
        """
        获取指定实体状态

        Args:
            entity_id: 实体 ID

        Returns:
            dict: 实体信息
        """
        # TODO: 从 pyCraft 获取实体状态
        return {
            "entity_id": entity_id,
            "type": "unknown",
            "position": (0, 0, 0),
            "health": 20.0,
        }

    async def get_inventory(self) -> list:
        """
        获取背包物品列表

        Returns:
            list: 物品列表
        """
        # TODO: 从 pyCraft 获取背包
        return []

    async def execute_action(self, action_type: str, **kwargs) -> Dict[str, Any]:
        """
        执行游戏动作

        Args:
            action_type: 动作类型 (move/dig/place/attack/eat/look)
            **kwargs: 动作参数

        Returns:
            dict: 执行结果 {"success": bool, "details": str}
        """
        if self._state != ConnectionState.CONNECTED:
            return {"success": False, "details": "未连接到服务器"}

        self.logger.debug(f"执行动作: {action_type} {kwargs}")

        # TODO: 调用 pyCraft 执行具体动作
        # 桩代码：返回成功
        return {"success": True, "details": f"动作 {action_type} 执行成功"}

    # ─── 重连机制 ───────────────────────────────────────────

    async def _reconnect_loop(self) -> None:
        """断线自动重连循环（指数退避）"""
        self._state = ConnectionState.RECONNECTING

        while self._state == ConnectionState.RECONNECTING:
            # 计算退避延迟
            delay = min(
                self._base_delay * (2 ** self._retry_count),
                self._max_retry_delay
            )
            self.logger.info(f"⏳ {delay} 秒后尝试重连 (第 {self._retry_count + 1} 次)...")
            await asyncio.sleep(delay)

            self._retry_count += 1
            await self.event_bus.emit(Event(
                type="connection.reconnecting",
                data={"attempt": self._retry_count, "delay": delay},
                source="connection"
            ))

            # 尝试重连
            success = await self.connect()
            if success:
                self.logger.info(f"✅ 重连成功 (第 {self._retry_count} 次)")
                return

            self.logger.warning(f"❌ 重连失败")

            # 检查是否超过最大重试次数（-1 = 无限）
            if (self.config.reconnect.max_retries > 0 and
                    self._retry_count >= self.config.reconnect.max_retries):
                self.logger.error("❌ 超过最大重试次数，停止重连")
                self._state = ConnectionState.DISCONNECTED
                await self.event_bus.emit(Event(
                    type="connection.failed",
                    data={"reason": "max_retries_exceeded"},
                    source="connection"
                ))
                return

    # ─── 心跳检测 ───────────────────────────────────────────

    async def _heartbeat_loop(self) -> None:
        """心跳检测循环"""
        while self._state == ConnectionState.CONNECTED:
            try:
                # TODO: 发送心跳包到 MC 服务器
                # self._client.send_keep_alive()

                self._last_heartbeat = time.time()
                await asyncio.sleep(15)  # 每 15 秒一次心跳

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"心跳失败: {e}")
                # 心跳失败，触发重连
                if self._state == ConnectionState.CONNECTED:
                    self._state = ConnectionState.DISCONNECTED
                    await self.event_bus.emit(Event(
                        type="connection.lost",
                        data={"reason": "heartbeat_failed"},
                        source="connection"
                    ))
                    if self.config.reconnect.enabled:
                        self._reconnect_task = asyncio.create_task(self._reconnect_loop())
                break

    # ─── 属性 ─────────────────────────────────────────────

    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._state == ConnectionState.CONNECTED

    @property
    def state(self) -> ConnectionState:
        """当前连接状态"""
        return self._state

    @property
    def info(self) -> ConnectionInfo:
        """连接信息"""
        return ConnectionInfo(
            server_ip=self.config.server_ip,
            server_port=self.config.server_port,
            username=self.config.username,
            version=self.config.version,
            state=self._state,
            connected_at=self._connected_at,
            last_heartbeat=self._last_heartbeat,
            reconnect_count=self._retry_count,
        )
