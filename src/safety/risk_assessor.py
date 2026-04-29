"""风险评估器"""
import logging
from typing import Dict


class RiskAssessor:
    """操作风险评估 — 返回 0-4 级"""

    DEFAULT_LEVELS = {
        "move": 0, "jump": 0, "chat": 0, "look_at": 0,
        "break_dirt": 1, "break_stone": 1, "place_torch": 1, "pickup_item": 1,
        "break_ore": 2, "attack_hostile": 2, "attack_neutral": 2, "dig_block": 2,
        "ignite_tnt": 3, "place_lava": 3, "break_chest": 3,
        "suicide": 4, "place_command_block": 4,
    }

    STRATEGIES = {
        0: "auto",    # 自动执行
        1: "auto",    # 自动执行
        2: "auto",    # 自动执行
        3: "ask",     # 需玩家授权
        4: "deny",    # 默认禁止
    }

    def __init__(self, custom_levels: Dict[str, int] = None):
        self.levels = {**self.DEFAULT_LEVELS}
        if custom_levels:
            self.levels.update(custom_levels)
        self.logger = logging.getLogger("blockmind.risk_assessor")

    def assess(self, action: str, context: dict = None) -> int:
        """评估操作风险等级"""
        level = self.levels.get(action, 1)  # 默认低风险
        self.logger.debug(f"风险评估: {action} -> 级别 {level}")
        return level

    def get_strategy(self, level: int) -> str:
        """获取授权策略"""
        return self.STRATEGIES.get(level, "ask")
