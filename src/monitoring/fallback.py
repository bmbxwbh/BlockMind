"""降级管理器 — 三级降级策略"""
import asyncio
import logging
from src.monitoring.alerter import Alerter


class FallbackManager:
    """降级管理器"""

    def __init__(self, alerter: Alerter, retry_count: int = 3):
        self.alerter = alerter
        self.retry_count = retry_count
        self.logger = logging.getLogger("blockmind.fallback")

    async def handle(self, error_level: int, context: dict, action_fn=None) -> bool:
        """
        处理错误

        1级 → 自动重试 N 次
        2级 → 终止任务，返回安全点
        3级 → 触发熔断（由 CircuitBreaker 处理）

        Returns: True=恢复成功, False=需要进一步处理
        """
        if error_level == 1:
            return await self._handle_level1(context, action_fn)
        elif error_level == 2:
            return await self._handle_level2(context)
        elif error_level == 3:
            return await self._handle_level3(context)
        return False

    async def _handle_level1(self, context: dict, action_fn) -> bool:
        """1级：自动重试"""
        skill_name = context.get("skill_name", "未知")
        await self.alerter.info(f"执行{skill_name}时遇到小问题，正在自动重试...")

        for attempt in range(1, self.retry_count + 1):
            self.logger.info(f"重试第 {attempt}/{self.retry_count} 次")
            if action_fn:
                try:
                    result = await action_fn()
                    if result:
                        await self.alerter.info(f"重试成功！")
                        return True
                except Exception as e:
                    self.logger.warning(f"重试失败: {e}")
            await asyncio.sleep(1 * attempt)  # 递增等待

        await self.alerter.warning(f"重试 {self.retry_count} 次后仍失败")
        return False

    async def _handle_level2(self, context: dict) -> bool:
        """2级：终止任务，返回安全点"""
        skill_name = context.get("skill_name", "未知")
        await self.alerter.warning(f"{skill_name}执行失败，已终止任务并返回安全点")
        # TODO: 调用 Mod API 传送到安全点
        return False

    async def _handle_level3(self, context: dict) -> bool:
        """3级：触发熔断（由 CircuitBreaker 处理）"""
        skill_name = context.get("skill_name", "未知")
        await self.alerter.emergency(f"{skill_name}执行出错！机器人处于危险状态，AI已接管")
        return False
