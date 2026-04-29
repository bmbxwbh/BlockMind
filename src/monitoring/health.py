"""健康检查器 — 定时检查系统各组件状态"""
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class HealthReport:
    """健康报告"""
    timestamp: datetime = field(default_factory=datetime.now)
    mod_connected: bool = False
    ai_connected: bool = False
    overall_healthy: bool = False
    details: dict = field(default_factory=dict)


class HealthChecker:
    """健康检查器"""

    def __init__(self, mod_client=None, ai_provider=None, interval: int = 10):
        self.mod_client = mod_client
        self.ai_provider = ai_provider
        self.interval = interval
        self._task: Optional[asyncio.Task] = None
        self._last_report = HealthReport()
        self.logger = logging.getLogger("blockmind.health")

    async def start(self) -> None:
        """启动定时检查"""
        self._task = asyncio.create_task(self._check_loop())
        self.logger.info(f"💓 健康检查启动 (间隔 {self.interval}s)")

    async def stop(self) -> None:
        """停止检查"""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def check_all(self) -> HealthReport:
        """执行全部检查"""
        report = HealthReport()
        report.mod_connected = await self.check_mod()
        report.ai_connected = await self.check_ai()
        report.overall_healthy = report.mod_connected and report.ai_connected
        self._last_report = report
        return report

    async def check_mod(self) -> bool:
        """检查 Mod 连接"""
        if not self.mod_client:
            return True
        try:
            return await self.mod_client.health_check()
        except Exception as e:
            self.logger.warning(f"Mod 健康检查失败: {e}")
            return False

    async def check_ai(self) -> bool:
        """检查 AI 连接"""
        if not self.ai_provider:
            return True
        try:
            return await self.ai_provider.health_check()
        except Exception as e:
            self.logger.warning(f"AI 健康检查失败: {e}")
            return False

    async def _check_loop(self) -> None:
        """定时检查循环"""
        while True:
            try:
                report = await self.check_all()
                if not report.overall_healthy:
                    self.logger.warning(f"⚠️ 系统不健康: mod={report.mod_connected} ai={report.ai_connected}")
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"健康检查异常: {e}")
                await asyncio.sleep(self.interval)

    @property
    def last_report(self) -> HealthReport:
        return self._last_report
