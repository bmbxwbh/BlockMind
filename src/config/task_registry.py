"""任务注册表 — 预定义所有已知任务的分类配置"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("blockmind.task_registry")


# 任务注册表：task_id → 任务配置
TASK_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ── L1 完全固定 ──
    "eat_food": {
        "level": "L1",
        "name": "进食",
        "aliases": ["吃东西", "进食", "吃饭"],
        "skill": "skills/builtin/survival/eat_food.yaml",
        "description": "自动寻找背包中的食物并进食",
    },
    "deposit_items": {
        "level": "L1",
        "name": "存放物品",
        "aliases": ["存东西", "存放物品", "存物品"],
        "skill": "skills/builtin/storage/deposit_items.yaml",
        "description": "将背包中的物品存放到最近的箱子",
    },
    "organize_chest": {
        "level": "L1",
        "name": "整理箱子",
        "aliases": ["整理箱子", "整理仓库"],
        "skill": "skills/builtin/storage/organize_chest.yaml",
        "description": "整理箱子中的物品，按类型分类",
    },
    "sleep": {
        "level": "L1",
        "name": "睡觉",
        "aliases": ["睡觉", "睡一觉"],
        "skill": "skills/builtin/survival/sleep.yaml",
        "description": "寻找床并睡觉",
    },
    "go_home": {
        "level": "L1",
        "name": "回家",
        "aliases": ["回家", "回基地"],
        "skill": "skills/builtin/navigation/go_home.yaml",
        "description": "返回基地/家的位置",
    },

    # ── L2 参数化 ──
    "chop_tree": {
        "level": "L2",
        "name": "砍树",
        "aliases": ["砍树", "伐木", "收集木材"],
        "skill": "skills/builtin/gathering/chop_tree.yaml",
        "params": ["tree_type"],
        "description": "砍伐指定类型的树木获取木材",
    },
    "mine_ore": {
        "level": "L2",
        "name": "挖矿",
        "aliases": ["挖矿", "采矿", "开矿"],
        "skill": "skills/builtin/gathering/mine_ore.yaml",
        "params": ["ore_type"],
        "description": "挖掘指定类型的矿石",
    },
    "farm_wheat": {
        "level": "L2",
        "name": "种田",
        "aliases": ["种田", "种小麦", "种地"],
        "skill": "skills/builtin/farming/plant_wheat.yaml",
        "params": [],
        "description": "种植和收割小麦",
    },
    "collect": {
        "level": "L2",
        "name": "采集",
        "aliases": ["采集", "收集", "捡东西"],
        "skill": "skills/builtin/gathering/collect.yaml",
        "params": ["target_type"],
        "description": "采集指定类型的物品",
    },
    "fish": {
        "level": "L2",
        "name": "钓鱼",
        "aliases": ["钓鱼"],
        "skill": "skills/builtin/gathering/fish.yaml",
        "params": [],
        "description": "使用钓鱼竿钓鱼",
    },
    "kill_mob": {
        "level": "L2",
        "name": "杀怪",
        "aliases": ["杀怪", "打怪", "清理怪物"],
        "skill": "skills/builtin/combat/kill_mob.yaml",
        "params": ["mob_type"],
        "description": "攻击指定类型的怪物",
    },

    # ── L3 模板化 ──
    "build_wall": {
        "level": "L3",
        "name": "建墙",
        "aliases": ["建墙", "砌墙"],
        "template": "build_wall",
        "params": ["length", "height", "material", "position"],
        "description": "建造一面墙",
    },
    "build_path": {
        "level": "L3",
        "name": "铺路",
        "aliases": ["铺路", "修路"],
        "template": "build_path",
        "params": ["start", "end", "material"],
        "description": "铺设一条道路",
    },

    # ── L4 动态（不预注册，每次 AI 推理） ──
}


class TaskRegistry:
    """任务注册表管理器"""

    def __init__(self):
        self._registry = dict(TASK_REGISTRY)

    def get(self, task_id: str) -> Optional[Dict[str, Any]]:
        """按 ID 获取任务配置"""
        return self._registry.get(task_id)

    def get_by_alias(self, alias: str) -> Optional[Dict[str, Any]]:
        """按别名查找任务"""
        for task_id, config in self._registry.items():
            if alias in config.get("aliases", []):
                return config
        return None

    def get_skill_path(self, task_id: str) -> Optional[str]:
        """获取任务对应的 Skill 文件路径"""
        config = self.get(task_id)
        if config:
            return config.get("skill")
        return None

    def register(self, task_id: str, config: Dict[str, Any]) -> None:
        """注册新任务"""
        self._registry[task_id] = config
        logger.info(f"注册任务: {task_id}")

    def unregister(self, task_id: str) -> bool:
        """取消注册"""
        if task_id in self._registry:
            del self._registry[task_id]
            return True
        return False

    def list_by_level(self, level: str) -> Dict[str, Dict[str, Any]]:
        """按级别列出任务"""
        return {k: v for k, v in self._registry.items() if v.get("level") == level}

    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """列出所有任务"""
        return dict(self._registry)
