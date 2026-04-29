"""寻路算法 — 基于 Mod API 的 A* 寻路"""

import heapq
import logging
import math
from typing import Optional, List, Tuple, Dict, Set

from src.mod_client.client import ModClient
from src.mod_client.models import BlockInfo

logger = logging.getLogger("blockmind.pathfinding")


def manhattan_distance(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> int:
    """曼哈顿距离"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def euclidean_distance(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    """欧几里得距离"""
    return math.sqrt(
        (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2
    )


# 可通行方块（非固体）
PASSABLE_BLOCKS = {
    "air", "cave_air", "void_air", "water", "flowing_water",
    "lava", "flowing_lava", "short_grass", "tall_grass", "fern",
    "dead_bush", "snow_layer", "torch", "wall_torch",
    "redstone_torch", "redstone_wall_torch", "lever",
    "flower_pot", "repeater", "comparator", "tripwire_hook",
    "button", "pressure_plate", "weighted_pressure_plate",
}

# 危险方块
DANGEROUS_BLOCKS = {"lava", "flowing_lava", "fire", "magma_block", "cactus"}


class Pathfinder:
    """寻路器

    使用 A* 算法在 Minecraft 世界中寻路。
    通过 Mod API 获取方块信息判断可通行性。
    """

    def __init__(self, mod_client: ModClient, max_search_radius: int = 64):
        self.mod_client = mod_client
        self.max_search_radius = max_search_radius
        self._block_cache: Dict[Tuple[int, int, int], str] = {}

    async def find_path(
        self,
        start: Tuple[int, int, int],
        goal: Tuple[int, int, int],
        max_iterations: int = 1000,
    ) -> Optional[List[Tuple[int, int, int]]]:
        """A* 寻路

        Args:
            start: 起点坐标 (x, y, z)
            goal: 终点坐标 (x, y, z)
            max_iterations: 最大迭代次数

        Returns:
            路径坐标列表，或 None（无法到达）
        """
        # 如果距离太远，直接直线移动
        if manhattan_distance(start, goal) > self.max_search_radius:
            logger.info("目标过远，使用直线移动")
            return [start, goal]

        open_set: List[Tuple[float, str, Tuple[int, int, int]]] = []
        heapq.heappush(open_set, (0, "start", start))

        came_from: Dict[Tuple[int, int, int], Tuple[int, int, int]] = {}
        g_score: Dict[Tuple[int, int, int], float] = {start: 0}
        closed: Set[Tuple[int, int, int]] = set()
        iterations = 0

        while open_set and iterations < max_iterations:
            iterations += 1
            _, _, current = heapq.heappop(open_set)

            if current == goal:
                return self._reconstruct_path(came_from, current)

            if current in closed:
                continue
            closed.add(current)

            for neighbor in self._get_neighbors(current):
                if neighbor in closed:
                    continue

                if not await self._is_passable(neighbor):
                    continue

                # 上下移动代价更高
                dy = abs(neighbor[1] - current[1])
                move_cost = 1.5 if dy > 0 else 1.0
                tentative_g = g_score[current] + move_cost

                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + manhattan_distance(neighbor, goal)
                    heapq.heappush(open_set, (f_score, f"n{iterations}", neighbor))

        logger.warning(f"寻路失败: ({start}) → ({goal}), 迭代={iterations}")
        return None

    def _get_neighbors(self, pos: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """获取相邻可移动位置（包含上下）"""
        x, y, z = pos
        neighbors = []
        # 水平四方向
        for dx, dz in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, nz = x + dx, z + dz
            neighbors.append((nx, y, nz))
            # 可以往上走一格
            neighbors.append((nx, y + 1, nz))
            # 可以往下走一格
            neighbors.append((nx, y - 1, nz))
        return neighbors

    async def _is_passable(self, pos: Tuple[int, int, int]) -> bool:
        """判断方块是否可通行"""
        # 检查缓存
        if pos in self._block_cache:
            block_type = self._block_cache[pos]
        else:
            blocks = await self.mod_client.get_blocks(radius=1)
            block_type = "air"  # 默认
            for b in blocks:
                bp = b.position
                bp_tuple = (bp.get("x", 0), bp.get("y", 0), bp.get("z", 0))
                if bp_tuple == pos:
                    block_type = b.type
                    break
            self._block_cache[pos] = block_type

        # 危险方块不可通行
        if block_type in DANGEROUS_BLOCKS:
            return False
        # 非固体方块可通行
        return block_type in PASSABLE_BLOCKS or not self._is_solid(block_type)

    @staticmethod
    def _is_solid(block_type: str) -> bool:
        """粗略判断方块是否固体"""
        non_solid = {
            "air", "water", "lava", "torch", "flower", "grass",
            "fern", "snow", "lever", "button", "pressure_plate",
            "redstone", "rail", "sign", "banner", "carpet",
        }
        return not any(ns in block_type for ns in non_solid)

    def _reconstruct_path(
        self,
        came_from: Dict[Tuple[int, int, int], Tuple[int, int, int]],
        current: Tuple[int, int, int],
    ) -> List[Tuple[int, int, int]]:
        """重建路径"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        logger.info(f"找到路径: {len(path)} 步")
        return path

    async def get_direction(
        self,
        current: Tuple[float, float, float],
        target: Tuple[float, float, float],
    ) -> Tuple[float, float, float]:
        """获取朝向目标的方向向量（归一化）"""
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        dz = target[2] - current[2]
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        if length == 0:
            return (0, 0, 0)
        return (dx / length, dy / length, dz / length)

    def clear_cache(self) -> None:
        """清空方块缓存"""
        self._block_cache.clear()
