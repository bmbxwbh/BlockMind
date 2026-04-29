"""熔断器 — 3级错误时立即停止所有动作"""
import asyncio
import logging
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"      # 正常
    OPEN = "open"          # 熔断中
    HALF_OPEN = "half_open" # 试探恢复


class CircuitBreaker:
    """熔断器"""

    def __init__(self, reset_timeout: int = 60):
        self.state = CircuitState.CLOSED
        self.reset_timeout = reset_timeout
        self._trip_count = 0
        self._last_trip_time = 0
        self.logger = logging.getLogger("blockmind.circuit_breaker")

    async def trip(self) -> None:
        """触发熔断"""
        self.state = CircuitState.OPEN
        self._trip_count += 1
        self.logger.error(f"🔴 熔断器触发！(第 {self._trip_count} 次)")

        # 定时尝试恢复
        await asyncio.sleep(self.reset_timeout)
        if self.state == CircuitState.OPEN:
            self.state = CircuitState.HALF_OPEN
            self.logger.info("🟡 熔断器进入半开状态，试探恢复...")

    async def reset(self) -> None:
        """重置熔断器"""
        self.state = CircuitState.CLOSED
        self.logger.info("🟢 熔断器已重置")

    @property
    def is_open(self) -> bool:
        """是否处于熔断状态"""
        return self.state == CircuitState.OPEN

    @property
    def is_half_open(self) -> bool:
        """是否处于半开状态"""
        return self.state == CircuitState.HALF_OPEN

    def allow_request(self) -> bool:
        """是否允许请求通过"""
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.HALF_OPEN:
            return True  # 允许试探
        return False
