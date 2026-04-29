"""环境感知 — 实时采集游戏世界状态

负责采集地形、实体、时间、天气等环境信息，
提供快捷查询接口，支持状态增量对比。
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


@dataclass
class WorldState:
    """世界状态快照"""
    dimension: str = "overworld"     # overworld / nether / the_end
    time_of_day: int = 0             # MC tick (0-24000)
    weather: str = "clear"           # clear / rain / thunder
    difficulty: str = "normal"
    day_count: int = 1


@dataclass
class EntityInfo:
    """实体信息"""
    entity_id: int
    entity_type: str                 # player / zombie / skeleton / cow / ...
    position: Tuple[float, float, float]
    health: float = 20.0
    distance: float = 0.0            # 与机器人的距离
    is_hostile: bool = False
    is_alive: bool = True


@dataclass
class BlockInfo:
    """方块信息"""
    position: Tuple[int, int, int]
    block_type: str                  # stone / dirt / diamond_ore / ...
    is_mineable: bool = True
    hardness: float = 1.0


@dataclass
class GameStateSnapshot:
    """完整游戏状态快照"""
    timestamp: datetime = field(default_factory=datetime.now)
    world: WorldState = field(default_factory=WorldState)
    player_health: float = 20.0
    player_hunger: float = 20.0
    player_position: Tuple[float, float, float] = (0.0, 64.0, 0.0)
    player_rotation: Tuple[float, float] = (0.0, 0.0)  # yaw, pitch
    player_experience: int = 0
    player_level: int = 0
    nearby_entities: List[EntityInfo] = field(default_factory=list)
    nearby_blocks: List[BlockInfo] = field(default_factory=list)


# 敌对生物列表
HOSTILE_MOBS = {
    "zombie", "skeleton", "spider", "creeper", "enderman",
    "witch", "blaze", "ghast", "slime", "magma_cube",
    "phantom", "drowned", "husk", "stray", "wither_skeleton",
    "guardian", "elder_guardian", "shulker", "vindicator",
    "evoker", "ravager", "pillager", "vex",
}


class StateCollector:
    """
    状态采集器

    功能：
    1. 定时采集完整游戏状态快照
    2. 增量对比：检测状态变化
    3. 提供快捷查询接口（附近实体、特定方块等）
    """

    def __init__(self, connection):
        """
        Args:
            connection: MCConnection 实例
        """
        self.connection = connection
        self.logger = logging.getLogger("blockmind.perception")
        self._last_snapshot: Optional[GameStateSnapshot] = None
        self._current_snapshot: Optional[GameStateSnapshot] = None

    async def collect(self) -> GameStateSnapshot:
        """
        采集当前完整游戏状态

        Returns:
            GameStateSnapshot: 完整状态快照
        """
        # 保存上一次快照用于对比
        self._last_snapshot = self._current_snapshot

        # 从连接获取数据
        world_data = await self.connection.get_world_state()
        entities_data = await self.connection.get_entity_state(0)  # 获取所有实体
        inventory_data = await self.connection.get_inventory()

        # 构建快照
        snapshot = GameStateSnapshot(
            timestamp=datetime.now(),
            world=WorldState(**world_data),
            # TODO: 从连接获取玩家状态
            player_health=20.0,
            player_hunger=20.0,
            player_position=(0.0, 64.0, 0.0),
            nearby_entities=self._parse_entities(entities_data),
            nearby_blocks=self._parse_blocks([]),  # TODO: 从连接获取方块
        )

        self._current_snapshot = snapshot
        return snapshot

    def _parse_entities(self, raw_data: Any) -> List[EntityInfo]:
        """解析实体数据"""
        # TODO: 从 pyCraft 数据解析实体
        return []

    def _parse_blocks(self, raw_data: Any) -> List[BlockInfo]:
        """解析方块数据"""
        # TODO: 从 pyCraft 数据解析方块
        return []

    # ─── 状态对比 ─────────────────────────────────────────

    def get_changed_fields(self) -> List[str]:
        """
        对比新旧快照，返回变化的字段名

        Returns:
            list: 变化的字段名列表
        """
        if not self._last_snapshot or not self._current_snapshot:
            return []

        changed = []
        curr = self._current_snapshot
        prev = self._last_snapshot

        # 简单字段对比
        if curr.player_health != prev.player_health:
            changed.append("player_health")
        if curr.player_hunger != prev.player_hunger:
            changed.append("player_hunger")
        if curr.player_position != prev.player_position:
            changed.append("player_position")
        if curr.world.time_of_day != prev.world.time_of_day:
            changed.append("world.time_of_day")
        if curr.world.weather != prev.world.weather:
            changed.append("world.weather")

        return changed

    # ─── 快捷查询 ─────────────────────────────────────────

    def has_hostile_nearby(self, radius: float = 16.0) -> bool:
        """
        检查附近是否有敌对生物

        Args:
            radius: 检测半径（方块）

        Returns:
            bool: 是否有敌对生物在范围内
        """
        if not self._current_snapshot:
            return False

        return any(
            entity.is_hostile and entity.distance <= radius
            for entity in self._current_snapshot.nearby_entities
        )

    def get_hostile_entities(self, radius: float = 32.0) -> List[EntityInfo]:
        """
        获取范围内的敌对生物

        Args:
            radius: 检测半径

        Returns:
            list: 敌对生物列表
        """
        if not self._current_snapshot:
            return []

        return [
            entity for entity in self._current_snapshot.nearby_entities
            if entity.is_hostile and entity.distance <= radius
        ]

    def get_nearest_entity(self, entity_type: str = None) -> Optional[EntityInfo]:
        """
        获取最近的指定类型实体

        Args:
            entity_type: 实体类型（None = 任意类型）

        Returns:
            EntityInfo 或 None
        """
        if not self._current_snapshot:
            return None

        entities = self._current_snapshot.nearby_entities
        if entity_type:
            entities = [e for e in entities if e.entity_type == entity_type]

        return min(entities, key=lambda e: e.distance) if entities else None

    def get_entities_in_radius(self, radius: float = 32.0,
                               entity_type: str = None,
                               hostile_only: bool = False) -> List[EntityInfo]:
        """
        获取范围内的实体

        Args:
            radius: 检测半径
            entity_type: 实体类型过滤
            hostile_only: 是否只返回敌对生物

        Returns:
            list: 实体列表
        """
        if not self._current_snapshot:
            return []

        entities = self._current_snapshot.nearby_entities

        if entity_type:
            entities = [e for e in entities if e.entity_type == entity_type]
        if hostile_only:
            entities = [e for e in entities if e.is_hostile]

        return [e for e in entities if e.distance <= radius]

    def get_blocks_by_type(self, block_type: str,
                           radius: int = 32) -> List[BlockInfo]:
        """
        获取指定范围内的特定类型方块

        Args:
            block_type: 方块类型
            radius: 检测半径

        Returns:
            list: 方块列表，按距离排序
        """
        if not self._current_snapshot:
            return []

        player_pos = self._current_snapshot.player_position
        blocks = [
            b for b in self._current_snapshot.nearby_blocks
            if b.block_type == block_type
        ]

        # 按距离排序
        def distance(block: BlockInfo) -> float:
            dx = block.position[0] - player_pos[0]
            dy = block.position[1] - player_pos[1]
            dz = block.position[2] - player_pos[2]
            return (dx*dx + dy*dy + dz*dz) ** 0.5

        blocks = [b for b in blocks if distance(b) <= radius]
        blocks.sort(key=distance)

        return blocks

    def get_nearest_block(self, block_type: str) -> Optional[BlockInfo]:
        """
        获取最近的指定类型方块

        Args:
            block_type: 方块类型

        Returns:
            BlockInfo 或 None
        """
        blocks = self.get_blocks_by_type(block_type)
        return blocks[0] if blocks else None

    # ─── 属性 ─────────────────────────────────────────────

    @property
    def current(self) -> Optional[GameStateSnapshot]:
        """当前状态快照"""
        return self._current_snapshot

    @property
    def player_position(self) -> Tuple[float, float, float]:
        """玩家当前位置"""
        if self._current_snapshot:
            return self._current_snapshot.player_position
        return (0.0, 64.0, 0.0)

    @property
    def player_health(self) -> float:
        """玩家生命值"""
        if self._current_snapshot:
            return self._current_snapshot.player_health
        return 20.0

    @property
    def player_hunger(self) -> float:
        """玩家饥饿值"""
        if self._current_snapshot:
            return self._current_snapshot.player_hunger
        return 20.0

    @property
    def is_night(self) -> bool:
        """是否是夜晚（13000-23000 tick）"""
        if self._current_snapshot:
            return 13000 <= self._current_snapshot.world.time_of_day <= 23000
        return False
