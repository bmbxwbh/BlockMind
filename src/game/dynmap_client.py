"""Dynmap 数据客户端 — 可选依赖

从 Dynmap HTTP API 获取地图数据：
- 玩家位置
- 方块数据
- 世界信息
- 标记点管理

Dynmap 默认运行在端口 8163，提供 REST API。
"""
import logging
import time
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import httpx

logger = logging.getLogger("blockmind.dynmap")


@dataclass
class DynmapPlayer:
    name: str
    world: str
    x: float
    y: float
    z: float
    health: float = 20.0
    armor: float = 0.0

    @property
    def position(self):
        return (self.x, self.y, self.z)


@dataclass
class DynmapMarker:
    name: str
    world: str
    x: float
    y: float
    z: float
    icon: str = "marker"
    label: str = ""


class DynmapClient:
    """Dynmap HTTP API 客户端"""

    def __init__(self, host: str = "localhost", port: int = 8163, api_key: str = ""):
        self.base_url = f"http://{host}:{port}"
        self.api_key = api_key
        self._connected = False
        self._last_check = 0
        self._check_interval = 30  # seconds

    async def check_connection(self) -> bool:
        """检查 Dynmap 是否在线"""
        if time.time() - self._last_check < self._check_interval:
            return self._connected

        self._last_check = time.time()
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{self.base_url}/upsert")
                self._connected = r.status_code in (200, 405)
        except Exception:
            self._connected = False

        return self._connected

    # ── 玩家数据 ─ ─

    async def get_players(self, world: str = None) -> List[DynmapPlayer]:
        """获取在线玩家位置"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self.base_url}/players/")
                if r.status_code == 200:
                    data = r.json()
                    players = []
                    for p in data.get("players", []):
                        if world and p.get("world") != world:
                            continue
                        players.append(DynmapPlayer(
                            name=p.get("name", ""),
                            world=p.get("world", "world"),
                            x=p.get("x", 0),
                            y=p.get("y", 0),
                            z=p.get("z", 0),
                            health=p.get("health", 20),
                            armor=p.get("armor", 0),
                        ))
                    return players
        except Exception as e:
            logger.debug(f"Failed to get players: {e}")
        return []

    async def get_player_position(self, name: str) -> Optional[tuple]:
        """获取指定玩家位置"""
        players = await self.get_players()
        for p in players:
            if p.name.lower() == name.lower():
                return p.position
        return None

    # ── 世界信息 ─ ─

    async def get_worlds(self) -> List[str]:
        """获取所有世界名称"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self.base_url}/tiles/")
                if r.status_code == 200:
                    # Parse world names from tile paths
                    return []
        except Exception:
            pass
        return []

    # ── 标记管理 ─ ─

    async def add_marker(self, marker: DynmapMarker, marker_set: str = "blockmind") -> bool:
        """添加或更新标记点"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                params = {
                    "world": marker.world,
                    "name": f"{marker_set}_{marker.name}",
                    "label": marker.label or marker.name,
                    "icon": marker.icon,
                    "x": str(int(marker.x)),
                    "y": str(int(marker.y)),
                    "z": str(int(marker.z)),
                }
                if self.api_key:
                    params["apikey"] = self.api_key

                r = await client.get(f"{self.base_url}/upsert", params=params)
                return r.status_code == 200
        except Exception as e:
            logger.debug(f"Failed to add marker: {e}")
        return False

    async def remove_marker(self, name: str, marker_set: str = "blockmind") -> bool:
        """删除标记点"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                params = {
                    "name": f"{marker_set}_{name}",
                }
                if self.api_key:
                    params["apikey"] = self.api_key

                r = await client.get(f"{self.base_url}/delete", params=params)
                return r.status_code == 200
        except Exception as e:
            logger.debug(f"Failed to remove marker: {e}")
        return False

    async def update_bot_position(self, bot_name: str, world: str, x: float, y: float, z: float) -> bool:
        """更新机器人位置标记"""
        return await self.add_marker(DynmapMarker(
            name=f"bot_{bot_name}",
            world=world,
            x=x, y=y, z=z,
            icon="marker",
            label=f"🤖 {bot_name}",
        ), marker_set="blockmind")

    async def add_zone_marker(self, zone_name: str, world: str, x: float, y: float, z: float,
                               zone_type: str = "info") -> bool:
        """添加区域标记（保护区、危险区等）"""
        icons = {
            "protect": "shield",
            "danger": "warning",
            "resource": "chest",
            "info": "info",
        }
        return await self.add_marker(DynmapMarker(
            name=f"zone_{zone_name}",
            world=world,
            x=x, y=y, z=z,
            icon=icons.get(zone_type, "marker"),
            label=f"{zone_type.upper()}: {zone_name}",
        ), marker_set="blockmind")

    # ── 方块数据（从 Dynmap 渲染结果读取） ─ ─

    async def get_tile(self, world: str, map_type: str, x: int, z: int) -> Optional[bytes]:
        """获取地图瓦片图片"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self.base_url}/tiles/{world}/{map_type}/{x}/{z}.png")
                if r.status_code == 200:
                    return r.content
        except Exception as e:
            logger.debug(f"Failed to get tile: {e}")
        return None
