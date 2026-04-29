"""Mod API 数据模型"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class PlayerStatus:
    """玩家状态"""
    connected: bool = False
    health: float = 20.0
    hunger: int = 20
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    rotation: Dict[str, float] = field(default_factory=lambda: {"yaw": 0, "pitch": 0})
    experience: int = 0
    level: int = 0
    dimension: str = "overworld"
    time_of_day: int = 0
    weather: str = "clear"

    @classmethod
    def from_dict(cls, data: dict) -> "PlayerStatus":
        return cls(
            connected=data.get("connected", False),
            health=data.get("health", 20.0),
            hunger=data.get("hunger", 20),
            position=data.get("position", {"x": 0, "y": 0, "z": 0}),
            rotation=data.get("rotation", {"yaw": 0, "pitch": 0}),
            experience=data.get("experience", 0),
            level=data.get("level", 0),
            dimension=data.get("dimension", "overworld"),
            time_of_day=data.get("time_of_day", 0),
            weather=data.get("weather", "clear"),
        )


@dataclass
class WorldState:
    """世界状态"""
    dimension: str = "overworld"
    time_of_day: int = 0
    weather: str = "clear"
    difficulty: str = "normal"
    day_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "WorldState":
        return cls(
            dimension=data.get("dimension", "overworld"),
            time_of_day=data.get("time_of_day", 0),
            weather=data.get("weather", "clear"),
            difficulty=data.get("difficulty", "normal"),
            day_count=data.get("day_count", 0),
        )


@dataclass
class InventoryItem:
    """背包物品"""
    name: str = ""
    slot: int = 0
    count: int = 0
    durability: int = 0
    max_durability: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "InventoryItem":
        return cls(
            name=data.get("name", ""),
            slot=data.get("slot", 0),
            count=data.get("count", 0),
            durability=data.get("durability", 0),
            max_durability=data.get("max_durability", 0),
        )


@dataclass
class InventoryState:
    """背包总览"""
    items: List[InventoryItem] = field(default_factory=list)
    empty_slots: int = 36
    is_full: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "InventoryState":
        items = [InventoryItem.from_dict(i) for i in data.get("items", [])]
        return cls(
            items=items,
            empty_slots=data.get("empty_slots", 36),
            is_full=data.get("is_full", False),
        )

    def count_item(self, item_name: str) -> int:
        """统计某物品总数"""
        return sum(i.count for i in self.items if i.name == item_name)

    def has_item(self, item_name: str, min_count: int = 1) -> bool:
        """是否拥有足够物品"""
        return self.count_item(item_name) >= min_count


@dataclass
class EntityInfo:
    """实体信息"""
    id: int = 0
    type: str = ""
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    health: float = 0.0
    distance: float = 0.0
    hostile: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "EntityInfo":
        return cls(
            id=data.get("id", 0),
            type=data.get("type", ""),
            position=data.get("position", {"x": 0, "y": 0, "z": 0}),
            health=data.get("health", 0.0),
            distance=data.get("distance", 0.0),
            hostile=data.get("hostile", False),
        )


@dataclass
class BlockInfo:
    """方块信息"""
    position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    type: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "BlockInfo":
        return cls(
            position=data.get("position", {"x": 0, "y": 0, "z": 0}),
            type=data.get("type", ""),
        )


@dataclass
class ActionResult:
    """动作执行结果"""
    success: bool = False
    details: str = ""
    error: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "ActionResult":
        return cls(
            success=data.get("success", False),
            details=data.get("details", ""),
            error=data.get("error", ""),
        )


@dataclass
class WSMessage:
    """WebSocket 事件消息"""
    type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "WSMessage":
        return cls(
            type=data.get("type", ""),
            data=data.get("data", {}),
        )
