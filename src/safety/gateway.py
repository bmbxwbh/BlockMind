"""安全网关 — 所有动作的统一入口"""
import logging
from src.safety.risk_assessor import RiskAssessor
from src.safety.permission import PermissionManager
from src.safety.authorizer import Authorizer
from src.safety.audit import AuditLogger
from src.core.event_bus import EventBus


class SafetyGateway:
    """安全网关 — 串联：风险评估 → 权限检查 → 授权 → 审计"""

    def __init__(self, event_bus: EventBus, config=None):
        self.risk_assessor = RiskAssessor(
            custom_levels=config.risk_levels if config else None
        )
        self.permission = PermissionManager()
        self.authorizer = Authorizer(event_bus)
        self.audit = AuditLogger()
        self.enabled = True
        self.logger = logging.getLogger("blockmind.safety_gateway")

    async def check(self, action: str, context: dict = None) -> bool:
        """检查操作是否允许"""
        if not self.enabled:
            return True

        # 1. 风险评估
        level = self.risk_assessor.assess(action, context)
        strategy = self.risk_assessor.get_strategy(level)

        # 2. 权限检查
        if self.permission.is_denied(action):
            self.audit.log(action, level, "denied_by_permission")
            return False

        # 3. 根据策略决定
        if strategy == "auto":
            self.audit.log(action, level, "auto_approved")
            return True

        if strategy == "deny":
            self.audit.log(action, level, "denied_by_policy")
            return False

        if strategy == "ask":
            approved = await self.authorizer.request_approval(action, context)
            self.audit.log(action, level, "approved" if approved else "denied_by_player")
            return approved

        return False

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False
