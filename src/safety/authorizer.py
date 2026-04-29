"""授权管理器 — 高风险操作等待玩家授权"""
import asyncio
import logging
from src.core.event_bus import EventBus, Event


class Authorizer:
    """授权管理器"""

    def __init__(self, event_bus: EventBus, timeout: int = 30):
        self.event_bus = event_bus
        self.timeout = timeout
        self._pending: asyncio.Future = None
        self.logger = logging.getLogger("blockmind.authorizer")

    async def request_approval(self, action: str, context: dict = None) -> bool:
        """请求玩家授权"""
        self.logger.info(f"⚠️ 请求授权: {action}")
        self._pending = asyncio.get_event_loop().create_future()

        await self.event_bus.emit(Event(
            type="safety.request",
            data={"action": action, "context": context},
            source="authorizer",
        ))

        try:
            result = await asyncio.wait_for(self._pending, timeout=self.timeout)
            return result
        except asyncio.TimeoutError:
            self.logger.warning(f"授权超时: {action}")
            return False
        finally:
            self._pending = None

    def approve(self) -> None:
        """玩家同意"""
        if self._pending and not self._pending.done():
            self._pending.set_result(True)

    def deny(self) -> None:
        """玩家拒绝"""
        if self._pending and not self._pending.done():
            self._pending.set_result(False)
