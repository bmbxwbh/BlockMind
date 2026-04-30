"""Fabric Mod HTTP 客户端 — 与 Mod API 通信的核心客户端"""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List

import aiohttp

from src.mod_client.models import (
    PlayerStatus, WorldState, InventoryState,
    EntityInfo, BlockInfo, ActionResult,
)

logger = logging.getLogger("blockmind.mod_client")

# Expected mod version — update when the Python side requires a newer mod API
EXPECTED_MOD_VERSION = "1.0.0"

# Connection state persistence path
CONNECTION_STATE_PATH = Path("data/connection_state.json")


class ModClient:
    """Fabric Mod HTTP 客户端

    通过 HTTP API 与 Minecraft 服务端的 BlockMind Fabric Mod 通信。
    Mod 暴露 RESTful API（端口 25580），提供状态查询和动作执行。

    Features:
    - Connection state persistence across restarts
    - Mod version detection and compatibility check
    - Health-check based connection validation
    """

    def __init__(self, host: str = "localhost", port: int = 25580, timeout: float = 10.0):
        self.base_url = f"http://{host}:{port}"
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
        self._mod_version: Optional[str] = None
        self._connection_state: dict = self._load_connection_state()
        logger.info(f"ModClient 初始化: {self.base_url}")

    # ── Connection State Persistence ──

    @staticmethod
    def _load_connection_state() -> dict:
        """Load persisted connection state from disk."""
        try:
            if CONNECTION_STATE_PATH.exists():
                with open(CONNECTION_STATE_PATH, "r", encoding="utf-8") as f:
                    state = json.load(f)
                logger.debug(f"已加载连接状态: {CONNECTION_STATE_PATH}")
                return state
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"读取连接状态失败: {e}")
        return {
            "last_connected_at": None,
            "last_disconnected_at": None,
            "last_health_status": None,
            "last_error": None,
            "total_connections": 0,
            "mod_version": None,
        }

    def _save_connection_state(self) -> None:
        """Persist current connection state to disk."""
        try:
            CONNECTION_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CONNECTION_STATE_PATH, "w", encoding="utf-8") as f:
                json.dump(self._connection_state, f, indent=2, ensure_ascii=False)
            logger.debug("连接状态已保存")
        except OSError as e:
            logger.warning(f"保存连接状态失败: {e}")

    def _update_state(self, **kwargs) -> None:
        """Update and persist connection state fields."""
        self._connection_state.update(kwargs)
        self._save_connection_state()

    @property
    def connection_state(self) -> dict:
        """Return a copy of the current persisted connection state."""
        return dict(self._connection_state)

    @property
    def last_connected_at(self) -> Optional[str]:
        return self._connection_state.get("last_connected_at")

    # ── Connection Lifecycle ──

    async def connect(self) -> bool:
        """建立 HTTP 连接会话"""
        if self._session and not self._session.closed:
            return True
        try:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
            # 验证连接
            healthy = await self.health_check()
            if healthy:
                logger.info("Mod API 连接成功")
                total = self._connection_state.get("total_connections", 0) + 1
                self._update_state(
                    last_connected_at=datetime.now(timezone.utc).isoformat(),
                    last_health_status="ok",
                    last_error=None,
                    total_connections=total,
                )
                # Check mod version after successful connection
                await self._check_mod_version()
                return True
            else:
                logger.warning("Mod API 健康检查失败")
                self._update_state(
                    last_health_status="fail",
                    last_error="health_check_failed",
                )
                await self.disconnect()
                return False
        except Exception as e:
            logger.error(f"Mod API 连接失败: {e}")
            self._update_state(
                last_error=str(e),
                last_health_status="error",
            )
            await self.disconnect()
            return False

    async def disconnect(self) -> None:
        """关闭连接"""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("Mod API 连接已关闭")
        self._session = None
        self._update_state(
            last_disconnected_at=datetime.now(timezone.utc).isoformat(),
        )

    @property
    def is_connected(self) -> bool:
        return self._session is not None and not self._session.closed

    async def _ensure_session(self) -> None:
        """确保会话可用"""
        if not self.is_connected:
            await self.connect()

    # ── Mod Version Detection ──

    @property
    def mod_version(self) -> Optional[str]:
        """Return the detected mod version, or None if not yet detected."""
        return self._mod_version

    async def _check_mod_version(self) -> None:
        """Query the mod version and compare with expected version."""
        try:
            result = await self._get("/api/version")
            if "error" in result:
                logger.debug("Mod 版本端点不可用（可能为旧版 Mod）")
                return

            self._mod_version = result.get("version", "unknown")
            self._update_state(mod_version=self._mod_version)
            logger.info(f"Mod 版本: {self._mod_version} (期望: {EXPECTED_MOD_VERSION})")

            if self._mod_version != EXPECTED_MOD_VERSION:
                logger.warning(
                    f"⚠️ Mod 版本不匹配! 检测到 {self._mod_version}，"
                    f"期望 {EXPECTED_MOD_VERSION}。部分功能可能不兼容。"
                )
        except Exception as e:
            logger.debug(f"Mod 版本检测跳过: {e}")

    async def get_mod_version_info(self) -> dict:
        """Public method to get mod version information.

        Returns:
            {"detected": str|None, "expected": str, "match": bool}
        """
        if self._mod_version is None and self.is_connected:
            await self._check_mod_version()
        return {
            "detected": self._mod_version,
            "expected": EXPECTED_MOD_VERSION,
            "match": self._mod_version == EXPECTED_MOD_VERSION if self._mod_version else None,
        }

    # ── HTTP Helpers ──

    async def _get(self, path: str, params: dict = None) -> dict:
        """GET 请求"""
        await self._ensure_session()
        url = f"{self.base_url}{path}"
        try:
            async with self._session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    text = await resp.text()
                    logger.error(f"GET {path} 失败 [{resp.status}]: {text}")
                    return {"error": text, "status": resp.status}
        except aiohttp.ClientError as e:
            logger.error(f"GET {path} 网络错误: {e}")
            return {"error": str(e)}

    async def _post(self, path: str, data: dict = None) -> dict:
        """POST 请求"""
        await self._ensure_session()
        url = f"{self.base_url}{path}"
        try:
            async with self._session.post(url, json=data or {}) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    text = await resp.text()
                    logger.error(f"POST {path} 失败 [{resp.status}]: {text}")
                    return {"success": False, "error": text}
        except aiohttp.ClientError as e:
            logger.error(f"POST {path} 网络错误: {e}")
            return {"success": False, "error": str(e)}

    # ── 健康检查 ──

    async def health_check(self) -> bool:
        """检查 Mod API 是否可用"""
        try:
            result = await self._get("/health")
            return result.get("status") == "ok"
        except Exception:
            return False

    # ── 状态查询 ──

    async def get_status(self) -> PlayerStatus:
        """获取玩家状态"""
        data = await self._get("/api/status")
        if "error" in data:
            return PlayerStatus()
        return PlayerStatus.from_dict(data)

    async def get_world(self) -> WorldState:
        """获取世界状态"""
        data = await self._get("/api/world")
        if "error" in data:
            return WorldState()
        return WorldState.from_dict(data)

    async def get_inventory(self) -> InventoryState:
        """获取背包信息"""
        data = await self._get("/api/inventory")
        if "error" in data:
            return InventoryState()
        return InventoryState.from_dict(data)

    async def get_entities(self, radius: int = 32) -> List[EntityInfo]:
        """获取附近实体"""
        data = await self._get("/api/entities", params={"radius": radius})
        if "error" in data:
            return []
        return [EntityInfo.from_dict(e) for e in data.get("entities", [])]

    async def get_blocks(self, radius: int = 32, block_type: str = None) -> List[BlockInfo]:
        """获取附近方块"""
        params = {"radius": radius}
        if block_type:
            params["type"] = block_type
        data = await self._get("/api/blocks", params=params)
        if "error" in data:
            return []
        return [BlockInfo.from_dict(b) for b in data.get("blocks", [])]

    # ── 动作执行 ──

    async def move(self, x: float, y: float, z: float, sprint: bool = False) -> ActionResult:
        """移动到指定位置"""
        data = await self._post("/api/move", {"x": x, "y": y, "z": z, "sprint": sprint})
        return ActionResult.from_dict(data)

    async def dig(self, x: int, y: int, z: int) -> ActionResult:
        """挖掘方块"""
        data = await self._post("/api/dig", {"x": x, "y": y, "z": z})
        return ActionResult.from_dict(data)

    async def place(self, item: str, x: int, y: int, z: int) -> ActionResult:
        """放置方块"""
        data = await self._post("/api/place", {"item": item, "x": x, "y": y, "z": z})
        return ActionResult.from_dict(data)

    async def attack(self, entity_id: int) -> ActionResult:
        """攻击实体"""
        data = await self._post("/api/attack", {"entity_id": entity_id})
        return ActionResult.from_dict(data)

    async def eat(self, item: str) -> ActionResult:
        """进食"""
        data = await self._post("/api/eat", {"item": item})
        return ActionResult.from_dict(data)

    async def look(self, x: float, y: float, z: float) -> ActionResult:
        """看向指定位置"""
        data = await self._post("/api/look", {"x": x, "y": y, "z": z})
        return ActionResult.from_dict(data)

    async def chat(self, message: str) -> ActionResult:
        """发送聊天消息"""
        data = await self._post("/api/chat", {"message": message})
        return ActionResult.from_dict(data)

    # ── 智能导航 ──

    async def navigate_goto(self, x: int, y: int, z: int,
                            exclusion_zones: list = None,
                            allow_break: bool = False,
                            allow_place: bool = False,
                            sprint: bool = False) -> dict:
        """智能导航到目标位置（通过 Baritone 或基础寻路）

        Args:
            x, y, z: 目标坐标
            exclusion_zones: 排除区域列表
            allow_break: 是否允许破坏方块
            allow_place: 是否允许放置方块
            sprint: 是否疾跑

        Returns:
            {"success": bool, "engine": "baritone"|"basic", "path": [...]}
        """
        data = {
            "x": x, "y": y, "z": z,
            "exclusion_zones": exclusion_zones or [],
            "allow_break": allow_break,
            "allow_place": allow_place,
            "sprint": sprint,
        }
        return await self._post("/api/navigate/goto", data)

    async def navigate_stop(self) -> dict:
        """停止当前导航"""
        return await self._post("/api/navigate/stop")

    async def navigate_status(self) -> dict:
        """获取寻路引擎状态"""
        return await self._get("/api/navigate/status")
