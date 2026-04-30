"""BlockMind 记忆系统 — 持久化游戏记忆，跨会话学习

三层记忆架构（对标 Hermes 记忆系统）：
1. 空间记忆：建筑保护区、危险区域、资源点、兴趣点
2. 路径记忆：成功路径缓存、失败路径黑名单、路径统计
3. 策略记忆：成功策略沉淀、失败策略记录、模式学习

记忆持久化到 JSON 文件，支持热加载和增量更新。
"""

import json
import logging
import time
import math
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

logger = logging.getLogger("blockmind.memory")


# ════════════════════════════════════════════════════════
# 数据模型
# ════════════════════════════════════════════════════════

class ZoneType(str, Enum):
    """区域类型"""
    BUILDING = "building"        # 玩家建筑（禁止破坏）
    DANGER = "danger"            # 危险区域（岩浆、悬崖等）
    RESOURCE = "resource"        # 资源点（矿洞、农场等）
    BASE = "base"                # 基地/家
    SPAWN = "spawn"              # 出生点
    FARM = "farm"                # 农场
    MINE = "mine"                # 矿洞
    CHEST = "chest"              # 箱子/仓库
    WAYPOINT = "waypoint"        # 路标点
    CUSTOM = "custom"            # 自定义


@dataclass
class Zone:
    """空间区域"""
    zone_id: str                          # 唯一标识
    name: str                             # 友好名称
    zone_type: ZoneType                   # 区域类型
    center: Tuple[int, int, int]          # 中心坐标
    radius: int = 10                      # 半径（方块数）
    breakable: bool = True                # 是否允许破坏方块
    placeable: bool = True                # 是否允许放置方块
    metadata: Dict = field(default_factory=dict)  # 附加数据
    created_at: float = field(default_factory=time.time)
    last_visited: float = 0.0
    visit_count: int = 0

    def contains(self, x: int, y: int, z: int) -> bool:
        """判断坐标是否在区域内"""
        cx, cy, cz = self.center
        dx, dy, dz = abs(x - cx), abs(y - cy), abs(z - cz)
        return max(dx, dy, dz) <= self.radius

    def distance_to(self, x: int, y: int, z: int) -> float:
        """计算到区域中心的距离"""
        import math
        cx, cy, cz = self.center
        return math.sqrt((x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2)


@dataclass
class CachedPath:
    """缓存路径"""
    path_id: str                          # 唯一标识
    start: Tuple[int, int, int]           # 起点
    end: Tuple[int, int, int]             # 终点
    waypoints: List[Tuple[int, int, int]] # 路径点列表
    distance: int = 0                     # 路径长度
    success_count: int = 0                # 成功次数
    fail_count: int = 0                   # 失败次数
    avg_time: float = 0.0                 # 平均耗时（秒）
    last_used: float = 0.0                # 最后使用时间
    created_at: float = field(default_factory=time.time)
    obstacles_encountered: List[str] = field(default_factory=list)  # 遇到的障碍

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.fail_count
        return self.success_count / total if total > 0 else 0.0

    @property
    def is_reliable(self) -> bool:
        """成功率 > 80% 且至少成功过 2 次"""
        return self.success_rate >= 0.8 and self.success_count >= 2


@dataclass
class StrategyRecord:
    """策略记录"""
    strategy_id: str                      # 唯一标识
    task_type: str                        # 任务类型（如 "goto", "mine", "build"）
    description: str                      # 策略描述
    action_sequence: List[Dict]           # 动作序列
    success_count: int = 0
    fail_count: int = 0
    avg_duration: float = 0.0             # 平均执行时长
    context_tags: List[str] = field(default_factory=list)  # 上下文标签
    created_at: float = field(default_factory=time.time)
    last_used: float = 0.0

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.fail_count
        return self.success_count / total if total > 0 else 0.0

    @property
    def score(self) -> float:
        """策略综合评分 (0~1): 成功率 + 使用频率 + 时效性"""
        total = self.success_count + self.fail_count
        if total == 0:
            return 0.0
        rate_score = self.success_rate * 0.6
        freq_score = min(math.log1p(total) / math.log1p(20), 1.0) * 0.2
        age_days = (time.time() - self.last_used) / 86400 if self.last_used else 999
        recency = max(0.0, 1.0 - age_days / 60.0) * 0.2
        return rate_score + freq_score + recency


@dataclass
class PlayerMemory:
    """玩家记忆"""
    player_name: str
    home_location: Optional[Tuple[int, int, int]] = None
    preferred_tools: Dict[str, str] = field(default_factory=dict)  # task -> tool
    chat_history_summary: str = ""
    last_seen: float = 0.0
    interaction_count: int = 0
    preferences: Dict = field(default_factory=dict)


@dataclass
class WorldMemory:
    """世界记忆"""
    world_name: str = "overworld"
    spawn_point: Optional[Tuple[int, int, int]] = None
    safe_points: List[Tuple[int, int, int]] = field(default_factory=list)
    known_biomes: Dict[str, Tuple[int, int, int]] = field(default_factory=dict)
    day_count: int = 0
    notable_events: List[Dict] = field(default_factory=list)


# ════════════════════════════════════════════════════════
# 核心记忆管理器
# ════════════════════════════════════════════════════════

class GameMemory:
    """BlockMind 游戏记忆系统

    对标 Hermes 的 memory + skill_manage 系统：
    - 空间记忆 → 保护建筑、标记危险
    - 路径记忆 → 缓存路径、避免重复寻路
    - 策略记忆 → 沉淀成功经验、学习失败教训
    - 玩家记忆 → 记住玩家偏好和习惯
    - 世界记忆 → 记住世界关键信息

    所有记忆持久化到 JSON 文件，跨会话保留。
    """

    def __init__(self, storage_path: str = "data/memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # 容量配置
        self.max_paths: int = 2000
        self.max_strategies: int = 500
        self.max_zones: int = 500
        self.capacity_warning_threshold: float = 0.85

        # 记忆存储
        self.zones: Dict[str, Zone] = {}
        self.paths: Dict[str, CachedPath] = {}
        self.strategies: Dict[str, StrategyRecord] = {}
        self.players: Dict[str, PlayerMemory] = {}
        self.world: WorldMemory = WorldMemory()

        # 内存索引（不持久化，运行时构建）
        self._spatial_index: Dict[str, List[str]] = {}  # "chunk_key" -> [zone_ids]
        self._path_index: Dict[str, List[str]] = {}     # "start_end" -> [path_ids]

        # 容量警告回调
        self._capacity_callbacks: List = []

        # 加载持久化数据
        self._load_all()

        logger.info(f"🧠 记忆系统初始化: "
                     f"{len(self.zones)} 区域, "
                     f"{len(self.paths)} 路径, "
                     f"{len(self.strategies)} 策略, "
                     f"{len(self.players)} 玩家")

        self._check_capacity()

    # ── 空间记忆 ──────────────────────────────────────

    def add_zone(self, zone: Zone) -> None:
        """添加空间区域"""
        self.zones[zone.zone_id] = zone
        self._update_spatial_index(zone)
        self._save_zones()
        logger.info(f"📍 新增区域: {zone.name} ({zone.zone_type.value}) "
                     f"@ {zone.center} r={zone.radius}")

    def remove_zone(self, zone_id: str) -> bool:
        """移除空间区域"""
        if zone_id in self.zones:
            zone = self.zones.pop(zone_id)
            self._remove_from_spatial_index(zone)
            self._save_zones()
            logger.info(f"🗑️ 移除区域: {zone.name}")
            return True
        return False

    def get_zone(self, zone_id: str) -> Optional[Zone]:
        """获取区域"""
        return self.zones.get(zone_id)

    def get_zones_by_type(self, zone_type: ZoneType) -> List[Zone]:
        """按类型获取区域"""
        return [z for z in self.zones.values() if z.zone_type == zone_type]

    def get_protection_zones(self) -> List[Zone]:
        """获取所有保护区（建筑、基地，不可破坏）"""
        return [z for z in self.zones.values() if not z.breakable]

    def is_in_protected_zone(self, x: int, y: int, z: int) -> bool:
        """判断坐标是否在保护区内"""
        return any(zone.contains(x, y, z) and not zone.breakable
                   for zone in self.zones.values())

    def is_in_danger_zone(self, x: int, y: int, z: int) -> bool:
        """判断坐标是否在危险区域"""
        return any(zone.contains(x, y, z) and zone.zone_type == ZoneType.DANGER
                   for zone in self.zones.values())

    def get_nearby_zones(self, x: int, y: int, z: int,
                         radius: int = 50) -> List[Zone]:
        """获取附近的区域"""
        nearby = []
        for zone in self.zones.values():
            if zone.distance_to(x, y, z) <= radius:
                nearby.append(zone)
        nearby.sort(key=lambda zone: zone.distance_to(x, y, z))
        return nearby

    def visit_zone(self, zone_id: str) -> None:
        """记录访问区域"""
        if zone_id in self.zones:
            zone = self.zones[zone_id]
            zone.last_visited = time.time()
            zone.visit_count += 1
            self._save_zones()

    def register_building(self, name: str, center: Tuple[int, int, int],
                          radius: int = 10, metadata: Optional[Dict] = None) -> Zone:
        """注册玩家建筑（自动设为保护区）"""
        zone = Zone(
            zone_id=f"building_{name.lower().replace(' ', '_')}",
            name=name,
            zone_type=ZoneType.BUILDING,
            center=center,
            radius=radius,
            breakable=False,  # 建筑保护区禁止破坏
            placeable=False,  # 建筑保护区禁止放置
            metadata=metadata or {},
        )
        self.add_zone(zone)
        return zone

    def register_base(self, name: str, center: Tuple[int, int, int],
                      radius: int = 30) -> Zone:
        """注册基地"""
        zone = Zone(
            zone_id=f"base_{name.lower().replace(' ', '_')}",
            name=name,
            zone_type=ZoneType.BASE,
            center=center,
            radius=radius,
            breakable=False,
            placeable=True,  # 基地内可以放置
            metadata={"is_home": True},
        )
        self.add_zone(zone)
        # 同时更新玩家记忆中的家位置
        for player in self.players.values():
            player.home_location = center
        return zone

    def register_resource(self, name: str, center: Tuple[int, int, int],
                          resource_type: str = "ore", radius: int = 20) -> Zone:
        """注册资源点"""
        zone = Zone(
            zone_id=f"resource_{name.lower().replace(' ', '_')}",
            name=name,
            zone_type=ZoneType.RESOURCE,
            center=center,
            radius=radius,
            breakable=True,
            metadata={"resource_type": resource_type},
        )
        self.add_zone(zone)
        return zone

    def register_danger(self, name: str, center: Tuple[int, int, int],
                        danger_type: str = "lava", radius: int = 15) -> Zone:
        """注册危险区域"""
        zone = Zone(
            zone_id=f"danger_{name.lower().replace(' ', '_')}",
            name=name,
            zone_type=ZoneType.DANGER,
            center=center,
            radius=radius,
            breakable=True,  # 可以绕过
            metadata={"danger_type": danger_type},
        )
        self.add_zone(zone)
        return zone

    # ── 路径记忆 ──────────────────────────────────────

    def cache_path(self, start: Tuple[int, int, int],
                   end: Tuple[int, int, int],
                   waypoints: List[Tuple[int, int, int]],
                   success: bool = True,
                   duration: float = 0.0,
                   obstacles: Optional[List[str]] = None) -> CachedPath:
        """缓存路径"""
        path_id = self._make_path_id(start, end)

        if path_id in self.paths:
            # 更新已有路径
            path = self.paths[path_id]
            if success:
                path.success_count += 1
                # 更新路径点（取最新的成功路径）
                path.waypoints = waypoints
            else:
                path.fail_count += 1
            # 更新平均耗时
            total = path.success_count + path.fail_count
            path.avg_time = (path.avg_time * (total - 1) + duration) / total
            path.last_used = time.time()
            if obstacles:
                path.obstacles_encountered.extend(obstacles)
        else:
            # 新路径
            path = CachedPath(
                path_id=path_id,
                start=start,
                end=end,
                waypoints=waypoints,
                distance=len(waypoints),
                success_count=1 if success else 0,
                fail_count=0 if success else 1,
                avg_time=duration,
                last_used=time.time(),
                obstacles_encountered=obstacles or [],
            )
            self.paths[path_id] = path

        self._save_paths()
        logger.info(f"🛤️ 路径缓存: {start} → {end} "
                     f"(成功率={path.success_rate:.0%}, 次数={path.success_count + path.fail_count})")
        return path

    def get_cached_path(self, start: Tuple[int, int, int],
                        end: Tuple[int, int, int]) -> Optional[CachedPath]:
        """获取缓存路径"""
        path_id = self._make_path_id(start, end)
        return self.paths.get(path_id)

    def get_reliable_paths(self) -> List[CachedPath]:
        """获取所有可靠路径（成功率>80%且至少成功2次）"""
        return [p for p in self.paths.values() if p.is_reliable]

    def blacklist_path(self, start: Tuple[int, int, int],
                       end: Tuple[int, int, int],
                       reason: str = "") -> None:
        """将路径加入黑名单（连续失败3次以上）"""
        path_id = self._make_path_id(start, end)
        if path_id in self.paths:
            path = self.paths[path_id]
            path.fail_count += 10  # 标记为不可靠
            if reason:
                path.obstacles_encountered.append(f"blacklisted: {reason}")
            self._save_paths()
            logger.warning(f"🚫 路径黑名单: {start} → {end} ({reason})")

    def get_paths_from(self, start: Tuple[int, int, int]) -> List[CachedPath]:
        """获取从某点出发的所有缓存路径"""
        return [p for p in self.paths.values()
                if p.start == start or self._close_enough(p.start, start, 5)]

    # ── 策略记忆 ──────────────────────────────────────

    def record_strategy(self, task_type: str, description: str,
                        action_sequence: List[Dict],
                        success: bool = True,
                        duration: float = 0.0,
                        context_tags: Optional[List[str]] = None) -> StrategyRecord:
        """记录策略（成功或失败）"""
        # 基于任务类型+动作序列生成 ID
        strategy_id = self._make_strategy_id(task_type, action_sequence)

        if strategy_id in self.strategies:
            strategy = self.strategies[strategy_id]
            if success:
                strategy.success_count += 1
            else:
                strategy.fail_count += 1
            total = strategy.success_count + strategy.fail_count
            strategy.avg_duration = (strategy.avg_duration * (total - 1) + duration) / total
            strategy.last_used = time.time()
        else:
            strategy = StrategyRecord(
                strategy_id=strategy_id,
                task_type=task_type,
                description=description,
                action_sequence=action_sequence,
                success_count=1 if success else 0,
                fail_count=0 if success else 1,
                avg_duration=duration,
                context_tags=context_tags or [],
                last_used=time.time(),
            )
            self.strategies[strategy_id] = strategy

        self._save_strategies()
        status = "✅" if success else "❌"
        logger.info(f"{status} 策略记录: {task_type} - {description} "
                     f"(成功率={strategy.success_rate:.0%})")
        return strategy

    def get_best_strategy(self, task_type: str,
                          context_tags: Optional[List[str]] = None) -> Optional[StrategyRecord]:
        """获取最佳策略（成功率最高 + 最近使用）"""
        candidates = [
            s for s in self.strategies.values()
            if s.task_type == task_type and s.success_rate >= 0.6
        ]
        if context_tags:
            # 优先匹配上下文标签
            tagged = [s for s in candidates
                      if any(t in s.context_tags for t in context_tags)]
            if tagged:
                candidates = tagged

        if not candidates:
            return None

        # 按成功率 * 使用次数排序
        candidates.sort(key=lambda s: (s.success_rate * s.success_count, s.last_used),
                        reverse=True)
        return candidates[0]

    def get_strategies_by_type(self, task_type: str) -> List[StrategyRecord]:
        """获取某类型的所有策略"""
        return [s for s in self.strategies.values() if s.task_type == task_type]

    # ── 玩家记忆 ──────────────────────────────────────

    def get_or_create_player(self, player_name: str) -> PlayerMemory:
        """获取或创建玩家记忆"""
        if player_name not in self.players:
            self.players[player_name] = PlayerMemory(player_name=player_name)
            self._save_players()
        return self.players[player_name]

    def update_player_home(self, player_name: str,
                           location: Tuple[int, int, int]) -> None:
        """更新玩家家位置"""
        player = self.get_or_create_player(player_name)
        player.home_location = location
        self._save_players()
        logger.info(f"🏠 玩家 {player_name} 家位置更新: {location}")

    def record_player_interaction(self, player_name: str) -> None:
        """记录玩家交互"""
        player = self.get_or_create_player(player_name)
        player.last_seen = time.time()
        player.interaction_count += 1
        self._save_players()

    def get_player_home(self, player_name: str) -> Optional[Tuple[int, int, int]]:
        """获取玩家家位置"""
        player = self.players.get(player_name)
        return player.home_location if player else None

    # ── 世界记忆 ──────────────────────────────────────

    def set_spawn_point(self, location: Tuple[int, int, int]) -> None:
        """设置出生点"""
        self.world.spawn_point = location
        self._save_world()
        logger.info(f"🌅 出生点设置: {location}")

    def add_safe_point(self, location: Tuple[int, int, int]) -> None:
        """添加安全点"""
        if location not in self.world.safe_points:
            self.world.safe_points.append(location)
            self._save_world()
            logger.info(f"🛡️ 安全点添加: {location}")

    def record_event(self, event_type: str, description: str,
                     location: Optional[Tuple[int, int, int]] = None,
                     metadata: Optional[Dict] = None) -> None:
        """记录重要事件"""
        event = {
            "type": event_type,
            "description": description,
            "location": location,
            "metadata": metadata or {},
            "timestamp": time.time(),
        }
        self.world.notable_events.append(event)
        # 只保留最近 100 个事件
        if len(self.world.notable_events) > 100:
            self.world.notable_events = self.world.notable_events[-100:]
        self._save_world()

    def get_nearest_safe_point(self, x: int, y: int, z: int) -> Optional[Tuple[int, int, int]]:
        """获取最近的安全点"""
        if not self.world.safe_points:
            return self.world.spawn_point
        return min(self.world.safe_points,
                   key=lambda p: math.sqrt((p[0]-x)**2 + (p[1]-y)**2 + (p[2]-z)**2))

    # ── 记忆管理功能 ────────────────────────────────

    def cleanup_old_paths(self, max_age_days: int = 30) -> int:
        """清理超过 max_age_days 天未使用的旧路径（保留可靠路径）。返回删除数量。"""
        cutoff = time.time() - max_age_days * 86400
        to_remove = [
            pid for pid, p in self.paths.items()
            if p.last_used < cutoff and not p.is_reliable
        ]
        for pid in to_remove:
            del self.paths[pid]
        if to_remove:
            self._save_paths()
            logger.info(f"🧹 清理旧路径: 删除 {len(to_remove)} 条 (>{max_age_days} 天)")
        return len(to_remove)

    def cleanup_low_scoring_strategies(self, min_score: float = 0.15) -> int:
        """自动清理低评分策略。返回删除数量。"""
        to_remove = [
            sid for sid, s in self.strategies.items()
            if s.score < min_score and (s.success_count + s.fail_count) >= 3
        ]
        for sid in to_remove:
            del self.strategies[sid]
        if to_remove:
            self._save_strategies()
            logger.info(f"🧹 清理低评分策略: 删除 {len(to_remove)} 个 (score<{min_score})")
        return len(to_remove)

    def compress_similar_paths(self, distance_threshold: int = 10) -> int:
        """合并相似路径（起点和终点在阈值范围内）。返回合并次数。"""
        if len(self.paths) < 2:
            return 0
        path_list = list(self.paths.values())
        merged_ids: Set[str] = set()
        merge_count = 0
        for i in range(len(path_list)):
            if path_list[i].path_id in merged_ids:
                continue
            for j in range(i + 1, len(path_list)):
                if path_list[j].path_id in merged_ids:
                    continue
                a, b = path_list[i], path_list[j]
                if (self._close_enough(a.start, b.start, distance_threshold) and
                        self._close_enough(a.end, b.end, distance_threshold)):
                    keeper, loser = (a, b) if a.success_rate >= b.success_rate else (b, a)
                    keeper.success_count += loser.success_count
                    keeper.fail_count += loser.fail_count
                    keeper.avg_time = (keeper.avg_time + loser.avg_time) / 2
                    keeper.obstacles_encountered.extend(loser.obstacles_encountered)
                    if loser.last_used > keeper.last_used:
                        keeper.waypoints = loser.waypoints
                    keeper.last_used = max(keeper.last_used, loser.last_used)
                    merged_ids.add(loser.path_id)
                    merge_count += 1
        for pid in merged_ids:
            del self.paths[pid]
        if merge_count:
            self._save_paths()
            logger.info(f"🗜️ 路径压缩: 合并 {merge_count} 对相似路径")
        return merge_count

    def export_memory(self) -> Dict[str, Any]:
        """导出全部记忆为 JSON 可序列化字典"""
        data: Dict[str, Any] = {
            "version": 1,
            "exported_at": time.time(),
            "zones": {}, "paths": {}, "strategies": {}, "players": {}, "world": {},
        }
        for k, v in self.zones.items():
            d = asdict(v)
            d["center"] = list(v.center)
            d["zone_type"] = v.zone_type.value
            data["zones"][k] = d
        for k, v in self.paths.items():
            d = asdict(v)
            d["start"] = list(v.start)
            d["end"] = list(v.end)
            d["waypoints"] = [list(w) for w in v.waypoints]
            data["paths"][k] = d
        for k, v in self.strategies.items():
            data["strategies"][k] = asdict(v)
        for k, v in self.players.items():
            d = asdict(v)
            if v.home_location:
                d["home_location"] = list(v.home_location)
            data["players"][k] = d
        wd = asdict(self.world)
        if self.world.spawn_point:
            wd["spawn_point"] = list(self.world.spawn_point)
        wd["safe_points"] = [list(p) for p in self.world.safe_points]
        data["world"] = wd
        logger.info(f"📦 记忆导出: {self.get_stats()}")
        return data

    def import_memory(self, data: Dict[str, Any], merge: bool = True) -> Dict[str, int]:
        """从 JSON 字典导入记忆。merge=True 合并，False 覆盖。返回导入统计。"""
        stats: Dict[str, int] = {"zones": 0, "paths": 0, "strategies": 0, "players": 0}
        if not merge:
            self.zones.clear()
            self.paths.clear()
            self.strategies.clear()
            self.players.clear()
            self._spatial_index.clear()
        for k, v in data.get("zones", {}).items():
            if merge and k in self.zones:
                continue
            v["center"] = tuple(v["center"])
            v["zone_type"] = ZoneType(v["zone_type"])
            self.zones[k] = Zone(**v)
            self._update_spatial_index(self.zones[k])
            stats["zones"] += 1
        for k, v in data.get("paths", {}).items():
            if merge and k in self.paths:
                continue
            v["start"] = tuple(v["start"])
            v["end"] = tuple(v["end"])
            v["waypoints"] = [tuple(w) for w in v["waypoints"]]
            self.paths[k] = CachedPath(**v)
            stats["paths"] += 1
        for k, v in data.get("strategies", {}).items():
            if merge and k in self.strategies:
                continue
            self.strategies[k] = StrategyRecord(**v)
            stats["strategies"] += 1
        for k, v in data.get("players", {}).items():
            if merge and k in self.players:
                continue
            if v.get("home_location"):
                v["home_location"] = tuple(v["home_location"])
            self.players[k] = PlayerMemory(**v)
            stats["players"] += 1
        wd = data.get("world")
        if wd:
            if wd.get("spawn_point"):
                wd["spawn_point"] = tuple(wd["spawn_point"])
            wd["safe_points"] = [tuple(p) for p in wd.get("safe_points", [])]
            if not merge:
                self.world = WorldMemory(**wd)
            else:
                for sp in wd.get("safe_points", []):
                    if sp not in self.world.safe_points:
                        self.world.safe_points.append(sp)
                self.world.notable_events.extend(wd.get("notable_events", []))
                if not self.world.spawn_point and wd.get("spawn_point"):
                    self.world.spawn_point = wd["spawn_point"]
        self._save_zones()
        self._save_paths()
        self._save_strategies()
        self._save_players()
        self._save_world()
        logger.info(f"📥 记忆导入完成: {stats}")
        return stats

    def register_capacity_callback(self, callback) -> None:
        """注册容量警告回调 callback(message: str)"""
        self._capacity_callbacks.append(callback)

    def _check_capacity(self) -> None:
        """检查容量，接近上限时发出警告"""
        warnings = []
        if self.max_paths:
            r = len(self.paths) / self.max_paths
            if r >= self.capacity_warning_threshold:
                warnings.append(f"路径记忆已达 {r:.0%} ({len(self.paths)}/{self.max_paths})")
        if self.max_strategies:
            r = len(self.strategies) / self.max_strategies
            if r >= self.capacity_warning_threshold:
                warnings.append(f"策略记忆已达 {r:.0%} ({len(self.strategies)}/{self.max_strategies})")
        if self.max_zones:
            r = len(self.zones) / self.max_zones
            if r >= self.capacity_warning_threshold:
                warnings.append(f"区域记忆已达 {r:.0%} ({len(self.zones)}/{self.max_zones})")
        if warnings:
            msg = "⚠️ 记忆容量警告: " + "; ".join(warnings)
            logger.warning(msg)
            for cb in self._capacity_callbacks:
                try:
                    cb(msg)
                except Exception:
                    pass

    def get_capacity_report(self) -> Dict[str, Any]:
        """获取容量报告"""
        return {
            "paths": {"count": len(self.paths), "max": self.max_paths,
                      "ratio": round(len(self.paths) / self.max_paths, 3) if self.max_paths else 0},
            "strategies": {"count": len(self.strategies), "max": self.max_strategies,
                           "ratio": round(len(self.strategies) / self.max_strategies, 3) if self.max_strategies else 0},
            "zones": {"count": len(self.zones), "max": self.max_zones,
                      "ratio": round(len(self.zones) / self.max_zones, 3) if self.max_zones else 0},
            "warning_threshold": self.capacity_warning_threshold,
        }

    # ── Baritone 集成：生成排除区域 ──────────────────

    def get_exclusion_zones(self) -> List[Dict]:
        """获取 Baritone 排除区域列表

        返回格式供 Python 导航层和 Java Mod 使用：
        [{"center": [x,y,z], "radius": N, "type": "no_break|no_place|avoid"}]
        """
        exclusions = []
        for zone in self.zones.values():
            if not zone.breakable:
                exclusions.append({
                    "center": list(zone.center),
                    "radius": zone.radius,
                    "type": "no_break",
                    "name": zone.name,
                })
            if not zone.placeable:
                exclusions.append({
                    "center": list(zone.center),
                    "radius": zone.radius,
                    "type": "no_place",
                    "name": zone.name,
                })
            if zone.zone_type == ZoneType.DANGER:
                exclusions.append({
                    "center": list(zone.center),
                    "radius": zone.radius,
                    "type": "avoid",
                    "name": zone.name,
                })
        return exclusions

    def get_navigate_context(self, start: Tuple[int, int, int],
                             end: Tuple[int, int, int]) -> Dict:
        """获取导航上下文（注入到寻路引擎）"""
        cached = self.get_cached_path(start, end)
        nearby_zones = self.get_nearby_zones(end[0], end[1], end[2], radius=50)

        return {
            "exclusion_zones": self.get_exclusion_zones(),
            "cached_path": cached.waypoints if cached and cached.is_reliable else None,
            "cached_success_rate": cached.success_rate if cached else 0.0,
            "nearby_protections": [
                {"name": z.name, "center": z.center, "radius": z.radius}
                for z in nearby_zones if not z.breakable
            ],
            "nearby_dangers": [
                {"name": z.name, "center": z.center, "radius": z.radius}
                for z in nearby_zones if z.zone_type == ZoneType.DANGER
            ],
        }

    # ── AI 决策上下文注入 ────────────────────────────

    def get_ai_context(self) -> str:
        """生成 AI 可读的记忆摘要（注入到 prompt）"""
        lines = ["[记忆系统]"]

        # 空间记忆摘要
        buildings = self.get_zones_by_type(ZoneType.BUILDING)
        bases = self.get_zones_by_type(ZoneType.BASE)
        dangers = self.get_zones_by_type(ZoneType.DANGER)
        resources = self.get_zones_by_type(ZoneType.RESOURCE)

        if bases:
            lines.append("基地:")
            for b in bases:
                lines.append(f"  - {b.name}: {b.center} (半径{b.radius})")

        if buildings:
            lines.append("建筑保护区（禁止破坏）:")
            for b in buildings:
                lines.append(f"  - {b.name}: {b.center} (半径{b.radius})")

        if dangers:
            lines.append("危险区域:")
            for d in dangers:
                lines.append(f"  - {d.name}: {d.center} ({d.metadata.get('danger_type', '未知')})")

        if resources:
            lines.append("已知资源点:")
            for r in resources:
                lines.append(f"  - {r.name}: {r.center} ({r.metadata.get('resource_type', '未知')})")

        # 可靠路径
        reliable = self.get_reliable_paths()
        if reliable:
            lines.append(f"已知可靠路径: {len(reliable)} 条")
            for p in reliable[:5]:  # 最多显示5条
                lines.append(f"  - {p.start} → {p.end} (成功率{p.success_rate:.0%})")

        # 策略记忆
        if self.strategies:
            best = [s for s in self.strategies.values() if s.success_rate >= 0.7]
            if best:
                lines.append(f"已验证策略: {len(best)} 个")
                for s in best[:5]:
                    lines.append(f"  - [{s.task_type}] {s.description} (成功率{s.success_rate:.0%})")

        return "\n".join(lines) if len(lines) > 1 else "[记忆系统] 暂无记忆"

    # ── 统计 ──────────────────────────────────────────

    def get_stats(self) -> Dict:
        """获取记忆系统统计"""
        return {
            "zones": len(self.zones),
            "protected_zones": len(self.get_protection_zones()),
            "cached_paths": len(self.paths),
            "reliable_paths": len(self.get_reliable_paths()),
            "strategies": len(self.strategies),
            "players": len(self.players),
            "events": len(self.world.notable_events),
            "capacity": self.get_capacity_report(),
        }

    # ── 持久化 ────────────────────────────────────────

    def _save_zones(self) -> None:
        data = {}
        for k, v in self.zones.items():
            d = asdict(v)
            d["center"] = list(v.center)
            d["zone_type"] = v.zone_type.value
            data[k] = d
        self._write_json("zones.json", data)

    def _save_paths(self) -> None:
        data = {}
        for k, v in self.paths.items():
            d = asdict(v)
            d["start"] = list(v.start)
            d["end"] = list(v.end)
            d["waypoints"] = [list(w) for w in v.waypoints]
            data[k] = d
        self._write_json("paths.json", data)

    def _save_strategies(self) -> None:
        data = {}
        for k, v in self.strategies.items():
            data[k] = asdict(v)
        self._write_json("strategies.json", data)

    def _save_players(self) -> None:
        data = {}
        for k, v in self.players.items():
            d = asdict(v)
            if v.home_location:
                d["home_location"] = list(v.home_location)
            data[k] = d
        self._write_json("players.json", data)

    def _save_world(self) -> None:
        d = asdict(self.world)
        if self.world.spawn_point:
            d["spawn_point"] = list(self.world.spawn_point)
        d["safe_points"] = [list(p) for p in self.world.safe_points]
        self._write_json("world.json", d)

    def _load_all(self) -> None:
        """加载所有持久化数据"""
        self._load_zones()
        self._load_paths()
        self._load_strategies()
        self._load_players()
        self._load_world()

    def _load_zones(self) -> None:
        data = self._read_json("zones.json")
        for k, v in data.items():
            v["center"] = tuple(v["center"])
            v["zone_type"] = ZoneType(v["zone_type"])
            self.zones[k] = Zone(**v)
            self._update_spatial_index(self.zones[k])

    def _load_paths(self) -> None:
        data = self._read_json("paths.json")
        for k, v in data.items():
            v["start"] = tuple(v["start"])
            v["end"] = tuple(v["end"])
            v["waypoints"] = [tuple(w) for w in v["waypoints"]]
            self.paths[k] = CachedPath(**v)
        self._check_capacity()

    def _load_strategies(self) -> None:
        data = self._read_json("strategies.json")
        for k, v in data.items():
            self.strategies[k] = StrategyRecord(**v)
        self._check_capacity()

    def _load_players(self) -> None:
        data = self._read_json("players.json")
        for k, v in data.items():
            if v.get("home_location"):
                v["home_location"] = tuple(v["home_location"])
            self.players[k] = PlayerMemory(**v)

    def _load_world(self) -> None:
        data = self._read_json("world.json")
        if data:
            if data.get("spawn_point"):
                data["spawn_point"] = tuple(data["spawn_point"])
            data["safe_points"] = [tuple(p) for p in data.get("safe_points", [])]
            self.world = WorldMemory(**data)

    def _write_json(self, filename: str, data) -> None:
        path = self.storage_path / filename
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存记忆失败 [{filename}]: {e}")

    def _read_json(self, filename: str) -> dict:
        path = self.storage_path / filename
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载记忆失败 [{filename}]: {e}")
            return {}

    # ── 备份 ──────────────────────────────────────────

    def backup(self) -> str:
        """备份记忆数据到 data/backups/，返回备份路径"""
        import shutil
        from datetime import datetime

        backup_dir = self.storage_path.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        dest = backup_dir / timestamp

        try:
            shutil.copytree(str(self.storage_path), str(dest), dirs_exist_ok=True)
            logger.info(f"记忆备份完成: {dest}")

            # 清理旧备份，只保留最近 10 个
            backups = sorted(backup_dir.iterdir())
            while len(backups) > 10:
                oldest = backups.pop(0)
                if oldest.is_dir():
                    shutil.rmtree(oldest)
                    logger.info(f"清理旧备份: {oldest}")

            return str(dest)
        except Exception as e:
            logger.error(f"记忆备份失败: {e}")
            return ""

    def get_backup_list(self) -> list:
        """获取备份列表"""
        backup_dir = self.storage_path.parent / "backups"
        if not backup_dir.exists():
            return []
        return sorted(
            [{"name": d.name, "path": str(d), "size": sum(f.stat().st_size for f in d.rglob("*") if f.is_file())}
             for d in backup_dir.iterdir() if d.is_dir()],
            key=lambda x: x["name"], reverse=True
        )

    # ── 内部工具 ──────────────────────────────────────

    @staticmethod
    def _make_path_id(start: Tuple, end: Tuple) -> str:
        return f"{start[0]},{start[1]},{start[2]}_{end[0]},{end[1]},{end[2]}"

    @staticmethod
    def _make_strategy_id(task_type: str, actions: List[Dict]) -> str:
        import hashlib
        key = f"{task_type}_{json.dumps(actions, sort_keys=True)}"
        return hashlib.md5(key.encode()).hexdigest()[:12]

    @staticmethod
    def _close_enough(a: Tuple, b: Tuple, threshold: int) -> bool:
        return abs(a[0]-b[0]) <= threshold and abs(a[2]-b[2]) <= threshold

    def _update_spatial_index(self, zone: Zone) -> None:
        chunk_key = f"{zone.center[0]//16}_{zone.center[2]//16}"
        if chunk_key not in self._spatial_index:
            self._spatial_index[chunk_key] = []
        if zone.zone_id not in self._spatial_index[chunk_key]:
            self._spatial_index[chunk_key].append(zone.zone_id)

    def _remove_from_spatial_index(self, zone: Zone) -> None:
        chunk_key = f"{zone.center[0]//16}_{zone.center[2]//16}"
        if chunk_key in self._spatial_index:
            if zone.zone_id in self._spatial_index[chunk_key]:
                self._spatial_index[chunk_key].remove(zone.zone_id)
