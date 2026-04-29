"""错误分级器 — 将运行时错误分为 1/2/3 级"""
import logging


class ErrorClassifier:
    """错误分级器"""

    # 1级：临时偶发
    LEVEL_1_PATTERNS = [
        "timeout", "connection_reset", "temporary",
        "rate_limit", "retry",
    ]

    # 2级：无法恢复但安全
    LEVEL_2_PATTERNS = [
        "permission_denied", "not_found", "invalid",
        "skill_failed", "action_failed",
    ]

    # 3级：危及安全
    LEVEL_3_PATTERNS = [
        "health_critical", "trapped", "falling",
        "drowning", "burning", "surrounded",
    ]

    def __init__(self):
        self.logger = logging.getLogger("blockmind.error_classifier")

    def classify(self, error: Exception, context: dict = None) -> int:
        """
        分类错误级别
        1级 = 临时偶发（自动重试）
        2级 = 无法恢复但安全（终止回安全点）
        3级 = 危及安全（紧急熔断+AI接管）
        """
        error_str = str(error).lower()
        context = context or {}

        # 检查生命值（游戏状态）
        health = context.get("health", 20)
        if health < 5:
            self.logger.warning(f"生命值过低 ({health})，判定为 3 级")
            return 3

        # 模式匹配
        for pattern in self.LEVEL_3_PATTERNS:
            if pattern in error_str:
                return 3

        for pattern in self.LEVEL_2_PATTERNS:
            if pattern in error_str:
                return 2

        for pattern in self.LEVEL_1_PATTERNS:
            if pattern in error_str:
                return 1

        # 默认 1 级
        return 1

    def get_level_name(self, level: int) -> str:
        """获取级别名称"""
        return {1: "临时偶发", 2: "无法恢复", 3: "危及安全"}.get(level, "未知")
