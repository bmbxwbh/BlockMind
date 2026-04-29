"""空闲任务池管理"""
import random
import logging
from typing import Optional, List, Dict
from dataclasses import dataclass


@dataclass
class IdleTask:
    """空闲任务"""
    name: str
    priority: int = 5
    enabled: bool = True
    skill_id: str = ""


class TaskPool:
    """空闲任务池"""

    # 默认任务池
    DEFAULT_TASKS = [
        IdleTask("farm_wheat", priority=5, skill_id="skill_plant_wheat_001"),
        IdleTask("mine_resources", priority=5, skill_id="skill_mine_ore_001"),
        IdleTask("chop_tree", priority=5, skill_id="skill_chop_tree_001"),
        IdleTask("organize_chest", priority=5, skill_id="skill_organize_chest_001"),
        IdleTask("repair_building", priority=4, skill_id="skill_repair_building_001"),
        IdleTask("place_torches", priority=4, skill_id="skill_place_torches_001"),
        IdleTask("patrol_area", priority=5, enabled=False, skill_id="skill_patrol_001"),
        IdleTask("deposit_items", priority=5, skill_id="skill_deposit_items_001"),
    ]

    def __init__(self):
        self._tasks: List[IdleTask] = list(self.DEFAULT_TASKS)
        self._last_task: Optional[str] = None
        self.logger = logging.getLogger("blockmind.task_pool")

    def get_next_task(self) -> Optional[IdleTask]:
        """获取下一个任务（优先级 + 随机轮转）"""
        enabled_tasks = [t for t in self._tasks if t.enabled]
        if not enabled_tasks:
            return None

        # 按优先级分组
        by_priority: Dict[int, List[IdleTask]] = {}
        for task in enabled_tasks:
            by_priority.setdefault(task.priority, []).append(task)

        # 选择最高优先级
        min_priority = min(by_priority.keys())
        candidates = by_priority[min_priority]

        # 避免连续执行同一任务
        if self._last_task and len(candidates) > 1:
            candidates = [t for t in candidates if t.name != self._last_task] or candidates

        chosen = random.choice(candidates)
        self._last_task = chosen.name
        return chosen

    def add_task(self, task: IdleTask) -> None:
        """添加任务"""
        self._tasks.append(task)

    def remove_task(self, name: str) -> None:
        """移除任务"""
        self._tasks = [t for t in self._tasks if t.name != name]

    def enable_task(self, name: str) -> None:
        """启用任务"""
        for task in self._tasks:
            if task.name == name:
                task.enabled = True

    def disable_task(self, name: str) -> None:
        """禁用任务"""
        for task in self._tasks:
            if task.name == name:
                task.enabled = False

    def list_tasks(self) -> List[IdleTask]:
        """列出所有任务"""
        return list(self._tasks)
