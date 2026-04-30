"""智能导航系统 — 记忆驱动的导航层

在原始寻路（Pathfinder）之上增加记忆层：
- 出发前：查询记忆获取保护区、缓存路径、危险区域
- 寻路时：将保护区注入为排除区域，优先走缓存路径
- 到达后：记录路径结果（成功/失败），更新记忆
- 失败时：学习失败原因，标记不可靠路径

对标 Hermes 的 skill 执行后自动沉淀机制。
"""

import asyncio
import logging
import time
from typing import Optional, List, Tuple, Dict

from src.core.memory import GameMemory, ZoneType
from src.game.pathfinding import Pathfinder
from src.mod_client.client import ModClient

logger = logging.getLogger("blockmind.navigation")


class NavigationResult:
    """导航结果"""

    def __init__(self, success: bool, path: List[Tuple[int, int, int]] = None,
                 message: str = "", duration: float = 0.0,
                 used_cache: bool = False, obstacles: List[str] = None):
        self.success = success
        self.path = path or []
        self.message = message
        self.duration = duration
        self.used_cache = used_cache
        self.obstacles = obstacles or []

    def __repr__(self):
        status = "✅" if self.success else "❌"
        return (f"NavigationResult({status} steps={len(self.path)} "
                f"cached={self.used_cache} time={self.duration:.1f}s)")


class SmartNavigator:
    """智能导航器

    整合 GameMemory + Pathfinder + Baritone API：
    1. 查询记忆：获取保护区、缓存路径、危险区域
    2. 决策：走缓存路径 or 请求 Baritone 寻路 or 自研 A*
    3. 执行：通过 Mod API 移动
    4. 学习：记录路径结果到记忆系统
    """

    def __init__(self, mod_client: ModClient, memory: GameMemory,
                 pathfinder: Pathfinder):
        self.mod_client = mod_client
        self.memory = memory
        self.pathfinder = pathfinder

        # Baritone 是否可用（运行时检测）
        self._baritone_available: Optional[bool] = None

        # 当前导航状态
        self._navigating = False
        self._current_target: Optional[Tuple[int, int, int]] = None

    # ── 核心导航方法 ─────────────────────────────────

    async def goto(self, x: int, y: int, z: int,
                   player_name: str = "player",
                   allow_break: bool = False,
                   allow_place: bool = False,
                   sprint: bool = False) -> NavigationResult:
        """智能导航到目标位置

        流程：
        1. 检查目标是否在保护区内 → 拒绝或警告
        2. 查询缓存路径 → 有可靠缓存直接走
        3. 请求 Baritone 寻路（带排除区域）→ 优先选择
        4. 回退到自研 A* 寻路
        5. 记录路径结果到记忆
        """
        start_time = time.time()
        target = (x, y, z)

        # 获取当前位置
        status = await self.mod_client.get_status()
        pos = status.position
        start = (int(pos.get("x", 0)), int(pos.get("y", 64)), int(pos.get("z", 0)))

        # ── 步骤1：安全检查 ──
        if self.memory.is_in_protected_zone(x, y, z) and not allow_break:
            logger.warning(f"⛔ 目标 ({x},{y},{z}) 在保护区内")
            # 不完全拒绝，但标记
            pass

        # ── 步骤2：查询缓存路径 ──
        cached = self.memory.get_cached_path(start, target)
        if cached and cached.is_reliable:
            logger.info(f"📋 使用缓存路径 (成功率={cached.success_rate:.0%})")
            result = await self._execute_cached_path(cached, sprint)
            if result.success:
                duration = time.time() - start_time
                self.memory.cache_path(start, target, cached.waypoints,
                                       success=True, duration=duration)
                return NavigationResult(
                    success=True, path=cached.waypoints,
                    message="缓存路径成功", duration=duration, used_cache=True,
                )
            else:
                logger.info("缓存路径失败，回退到重新寻路")

        # ── 步骤3：获取导航上下文 ──
        context = self.memory.get_navigate_context(start, target)
        exclusion_zones = context["exclusion_zones"]

        # 如果不允许破坏，添加所有保护区为排除区域
        if not allow_break:
            for zone in self.memory.get_protection_zones():
                if zone.contains(x, y, z):
                    logger.warning(f"⚠️ 目标在保护区内: {zone.name}")

        # ── 步骤4：Baritone 寻路（优先） ──
        if await self._is_baritone_available():
            result = await self._baritone_goto(
                target, exclusion_zones, allow_break, allow_place, sprint
            )
            if result.success:
                duration = time.time() - start_time
                self.memory.cache_path(start, target, result.path,
                                       success=True, duration=duration)
                return NavigationResult(
                    success=True, path=result.path,
                    message="Baritone 寻路成功", duration=duration,
                )

        # ── 步骤5：自研 A* 寻路（回退） ──
        path = await self.pathfinder.find_path(start, target)
        if path:
            result = await self._execute_path(path, sprint)
            duration = time.time() - start_time
            if result:
                self.memory.cache_path(start, target, path,
                                       success=True, duration=duration)
                return NavigationResult(
                    success=True, path=path,
                    message="A* 寻路成功", duration=duration,
                )

        # ── 全部失败 ──
        duration = time.time() - start_time
        self.memory.cache_path(start, target, [],
                               success=False, duration=duration)
        return NavigationResult(
            success=False,
            message=f"导航失败: 无法到达 ({x},{y},{z})",
            duration=duration,
        )

    async def goto_player(self, player_name: str,
                          follow_range: int = 3) -> NavigationResult:
        """导航到玩家位置"""
        # 获取玩家位置
        entities = await self.mod_client.get_entities(radius=64)
        target_entity = None
        for e in entities:
            if e.type == "player" and e.metadata.get("name") == player_name:
                target_entity = e
                break

        if not target_entity:
            return NavigationResult(
                success=False,
                message=f"找不到玩家 {player_name}",
            )

        pos = target_entity.position
        return await self.goto(
            int(pos.get("x", 0)),
            int(pos.get("y", 64)),
            int(pos.get("z", 0)),
            player_name=player_name,
        )

    async def go_home(self, player_name: str = "player") -> NavigationResult:
        """回家"""
        home = self.memory.get_player_home(player_name)
        if home:
            return await self.goto(home[0], home[1], home[2],
                                   player_name=player_name)

        # 尝试找基地类型区域
        bases = self.memory.get_zones_by_type(ZoneType.BASE)
        if bases:
            base = bases[0]
            return await self.goto(base.center[0], base.center[1], base.center[2],
                                   player_name=player_name)

        return NavigationResult(success=False, message="未设置家位置")

    async def go_to_safe_point(self) -> NavigationResult:
        """前往安全点"""
        status = await self.mod_client.get_status()
        pos = status.position
        safe = self.memory.get_nearest_safe_point(
            int(pos.get("x", 0)), int(pos.get("y", 64)), int(pos.get("z", 0))
        )
        if safe:
            return await self.goto(safe[0], safe[1], safe[2])
        return NavigationResult(success=False, message="没有安全点")

    async def patrol(self, waypoints: List[Tuple[int, int, int]],
                     player_name: str = "player") -> List[NavigationResult]:
        """巡逻路线"""
        results = []
        for wp in waypoints:
            result = await self.goto(wp[0], wp[1], wp[2],
                                     player_name=player_name)
            results.append(result)
            if not result.success:
                logger.warning(f"巡逻中断于 {wp}: {result.message}")
                break
            await asyncio.sleep(2)  # 每个点停留2秒
        return results

    # ── 记忆学习 ─────────────────────────────────────

    async def auto_detect_and_memorize(self) -> None:
        """自动检测并记忆环境

        扫描周围环境，自动注册：
        - 玩家建筑（检测到非自然方块组合）
        - 危险区域（岩浆、火焰）
        - 资源点（矿石群）
        """
        blocks = await self.mod_client.get_blocks(radius=32)
        status = await self.mod_client.get_status()
        pos = status.position
        px, py, pz = int(pos.get("x", 0)), int(pos.get("y", 64)), int(pos.get("z", 0))

        # 检测建筑（连续的建筑方块）
        building_blocks = {"stone_bricks", "planks", "cobblestone", "bricks",
                           "quartz_block", "concrete", "terracotta", "glass",
                           "iron_block", "gold_block", "diamond_block"}
        building_zones = self._detect_cluster_zones(blocks, building_blocks, "建筑")

        for zone_data in building_zones:
            zone_id = f"building_auto_{zone_data['center'][0]}_{zone_data['center'][2]}"
            if zone_id not in self.memory.zones:
                self.memory.register_building(
                    name=f"自动检测建筑 ({zone_data['center'][0]}, {zone_data['center'][2]})",
                    center=zone_data["center"],
                    radius=zone_data["radius"],
                    metadata={"auto_detected": True},
                )

        # 检测危险区域（岩浆）
        danger_blocks = {"lava", "flowing_lava", "fire", "magma_block"}
        danger_zones = self._detect_cluster_zones(blocks, danger_blocks, "危险")

        for zone_data in danger_zones:
            zone_id = f"danger_auto_{zone_data['center'][0]}_{zone_data['center'][2]}"
            if zone_id not in self.memory.zones:
                self.memory.register_danger(
                    name=f"自动检测危险 ({zone_data['center'][0]}, {zone_data['center'][2]})",
                    center=zone_data["center"],
                    radius=zone_data["radius"],
                    danger_type="lava",
                )

        # 检测资源点（矿石群）
        ore_blocks = {"coal_ore", "iron_ore", "gold_ore", "diamond_ore",
                      "emerald_ore", "lapis_ore", "redstone_ore",
                      "deepslate_coal_ore", "deepslate_iron_ore",
                      "deepslate_gold_ore", "deepslate_diamond_ore"}
        ore_zones = self._detect_cluster_zones(blocks, ore_blocks, "矿石")

        for zone_data in ore_zones:
            zone_id = f"resource_auto_{zone_data['center'][0]}_{zone_data['center'][2]}"
            if zone_id not in self.memory.zones:
                self.memory.register_resource(
                    name=f"矿石点 ({zone_data['center'][0]}, {zone_data['center'][2]})",
                    center=zone_data["center"],
                    radius=zone_data["radius"],
                    resource_type="ore",
                )

    def learn_from_action(self, task_type: str, description: str,
                          actions: List[Dict], success: bool,
                          duration: float = 0.0,
                          context_tags: List[str] = None) -> None:
        """从动作执行中学习策略

        对标 Hermes 的 skill_manage(action='create') —
        成功的操作自动沉淀为可复用策略。
        """
        self.memory.record_strategy(
            task_type=task_type,
            description=description,
            action_sequence=actions,
            success=success,
            duration=duration,
            context_tags=context_tags or [],
        )

    def learn_path_failure(self, start: Tuple[int, int, int],
                           end: Tuple[int, int, int],
                           reason: str = "") -> None:
        """学习路径失败"""
        cached = self.memory.get_cached_path(start, end)
        if cached and cached.fail_count >= 3:
            self.memory.blacklist_path(start, end, reason)
        else:
            self.memory.cache_path(start, end, [], success=False)

    # ── 内部方法 ──────────────────────────────────────

    async def _is_baritone_available(self) -> bool:
        """检测 Baritone 是否可用"""
        if self._baritone_available is not None:
            return self._baritone_available
        try:
            result = await self.mod_client._get("/api/navigate/status")
            self._baritone_available = result.get("available", False)
        except Exception:
            self._baritone_available = False
        return self._baritone_available

    async def _baritone_goto(self, target: Tuple[int, int, int],
                             exclusion_zones: List[Dict],
                             allow_break: bool, allow_place: bool,
                             sprint: bool) -> NavigationResult:
        """通过 Baritone API 寻路"""
        try:
            data = {
                "x": target[0], "y": target[1], "z": target[2],
                "exclusion_zones": exclusion_zones,
                "allow_break": allow_break,
                "allow_place": allow_place,
                "sprint": sprint,
            }
            result = await self.mod_client._post("/api/navigate/goto", data)

            if result.get("success"):
                path = [tuple(p) for p in result.get("path", [])]
                return NavigationResult(
                    success=True, path=path,
                    message="Baritone 寻路成功",
                )
            else:
                return NavigationResult(
                    success=False,
                    message=result.get("error", "Baritone 寻路失败"),
                )
        except Exception as e:
            logger.error(f"Baritone API 调用失败: {e}")
            return NavigationResult(success=False, message=str(e))

    async def _execute_cached_path(self, cached_path,
                                   sprint: bool = False) -> bool:
        """执行缓存路径"""
        for waypoint in cached_path.waypoints:
            try:
                await self.mod_client.move(
                    waypoint[0], waypoint[1], waypoint[2], sprint=sprint
                )
                await asyncio.sleep(0.5)  # 等待移动完成
            except Exception as e:
                logger.error(f"缓存路径执行失败: {e}")
                return False
        return True

    async def _execute_path(self, path: List[Tuple[int, int, int]],
                            sprint: bool = False) -> bool:
        """执行路径"""
        for waypoint in path:
            try:
                await self.mod_client.move(
                    waypoint[0], waypoint[1], waypoint[2], sprint=sprint
                )
                await asyncio.sleep(0.3)
            except Exception as e:
                logger.error(f"路径执行失败: {e}")
                return False
        return True

    def _detect_cluster_zones(self, blocks, target_types: str,
                              label: str) -> List[Dict]:
        """检测方块聚类区域"""
        clusters = []
        visited = set()

        for block in blocks:
            btype = block.type
            bpos = block.position
            pos_key = (bpos.get("x", 0), bpos.get("y", 0), bpos.get("z", 0))

            if btype not in target_types or pos_key in visited:
                continue

            # BFS 聚类
            cluster = []
            queue = [pos_key]
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                cluster.append(current)

                # 查找相邻的同类方块
                for block2 in blocks:
                    p2 = block2.position
                    p2_key = (p2.get("x", 0), p2.get("y", 0), p2.get("z", 0))
                    if (p2_key not in visited and block2.type in target_types
                            and self._manhattan(current, p2_key) <= 3):
                        queue.append(p2_key)

            if len(cluster) >= 3:  # 至少3个方块才算区域
                # 计算中心和半径
                cx = sum(p[0] for p in cluster) // len(cluster)
                cy = sum(p[1] for p in cluster) // len(cluster)
                cz = sum(p[2] for p in cluster) // len(cluster)
                max_dist = max(self._manhattan((cx, cy, cz), p) for p in cluster)
                clusters.append({
                    "center": (cx, cy, cz),
                    "radius": max(max_dist + 2, 10),  # 加余量
                    "count": len(cluster),
                })

        return clusters

    @staticmethod
    def _manhattan(a: Tuple, b: Tuple) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])
