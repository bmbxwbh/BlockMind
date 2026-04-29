"""背包管理器 — 通过 Mod API 管理物品"""

import logging
from typing import Optional, List, Dict

from src.mod_client.client import ModClient
from src.mod_client.models import InventoryState, InventoryItem

logger = logging.getLogger("blockmind.inventory")


class InventoryManager:
    """背包管理器

    封装 Mod API 的背包查询，提供高级物品管理接口。
    自动缓存背包状态，支持手动刷新。
    """

    def __init__(self, mod_client: ModClient):
        self.mod_client = mod_client
        self._cache: Optional[InventoryState] = None

    async def refresh(self) -> InventoryState:
        """刷新背包缓存"""
        self._cache = await self.mod_client.get_inventory()
        logger.debug(f"背包刷新: {len(self._cache.items)} 物品, {self._cache.empty_slots} 空位")
        return self._cache

    @property
    def state(self) -> InventoryState:
        """获取缓存的背包状态"""
        if self._cache is None:
            return InventoryState()
        return self._cache

    def count(self, item_name: str) -> int:
        """统计某物品总数"""
        return self.state.count_item(item_name)

    def has_item(self, item_name: str, min_count: int = 1) -> bool:
        """是否拥有足够物品"""
        return self.state.has_item(item_name, min_count)

    def is_full(self) -> bool:
        """背包是否已满"""
        return self.state.is_full

    def get_empty_slots(self) -> int:
        """获取空位数"""
        return self.state.empty_slots

    def get_items_by_name(self, item_name: str) -> List[InventoryItem]:
        """按名称查找物品"""
        return [i for i in self.state.items if i.name == item_name]

    def get_low_durability_items(self, threshold: float = 0.2) -> List[InventoryItem]:
        """获取耐久度低的物品"""
        result = []
        for item in self.state.items:
            if item.max_durability > 0:
                ratio = item.durability / item.max_durability
                if ratio < threshold:
                    result.append(item)
        return result

    def get_summary(self) -> Dict[str, int]:
        """背包摘要：物品名 → 数量"""
        summary: Dict[str, int] = {}
        for item in self.state.items:
            summary[item.name] = summary.get(item.name, 0) + item.count
        return summary

    def total_item_count(self) -> int:
        """背包中物品总数"""
        return sum(i.count for i in self.state.items)
