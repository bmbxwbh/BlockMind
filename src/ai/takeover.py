"""AI 紧急接管模块"""
import logging
from typing import List, Dict
from src.ai.provider import AIProvider
from src.ai.prompts import PROMPTS


class EmergencyTakeover:
    """紧急接管 — 3级错误时 AI 直接控制机器人"""

    def __init__(self, provider: AIProvider, action_executor):
        self.provider = provider
        self.executor = action_executor
        self.active = False
        self.logger = logging.getLogger("blockmind.takeover")

    async def activate(self, context: dict) -> None:
        """激活紧急接管"""
        self.active = True
        self.logger.warning("🚨 紧急接管已激活")

    async def generate_actions(self, context: dict) -> List[Dict]:
        """AI 生成紧急动作"""
        prompt = PROMPTS["emergency_takeover"].format(context_snapshot=str(context))
        result = await self.provider.chat([{"role": "user", "content": prompt}], max_tokens=500)

        if "SAFE" in result:
            return [{"action": "safe", "details": "已安全"}]

        # 解析动作指令
        actions = []
        for line in result.strip().split("\n"):
            line = line.strip()
            if line.startswith("walk_to"):
                actions.append({"action": "walk_to", "args": line})
            elif line.startswith("eat"):
                actions.append({"action": "eat", "args": line})
        return actions

    async def deactivate(self) -> None:
        """关闭紧急接管"""
        self.active = False
        self.logger.info("✅ 紧急接管已关闭")
