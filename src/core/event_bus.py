"""事件总线 — 发布/订阅模式，模块间解耦通信"""
import asyncio
import logging
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("blockmind.event_bus")


@dataclass
class Event:
    """事件数据"""
    type: str              # 事件类型
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""       # 事件来源模块


class EventBus:
    """
    异步事件总线

    用法：
        bus = EventBus()
        bus.subscribe("task.completed", my_handler)
        await bus.emit(Event(type="task.completed", data={"skill_id": "xxx"}))

    事件类型规范：
        task.started / task.completed / task.failed
        skill.generated / skill.repaired
        error.detected / error.classified
        safety.request / safety.approved / safety.denied
        takeover.started / takeover.ended
        idle.started / idle.ended
        status.changed
    """

    def __init__(self, max_history: int = 100):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._history: List[Event] = []
        self._max_history = max_history

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """订阅事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"订阅事件: {event_type} -> {handler.__name__}")

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """取消订阅"""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                h for h in self._subscribers[event_type] if h != handler
            ]

    async def emit(self, event: Event) -> None:
        """发布事件，通知所有订阅者"""
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        handlers = self._subscribers.get(event.type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"事件处理异常 [{event.type}]: {e}")

    def get_history(self, event_type: Optional[str] = None, limit: int = 50) -> List[Event]:
        """获取事件历史"""
        events = self._history
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:]

    def clear_history(self) -> None:
        """清空事件历史"""
        self._history.clear()

    @property
    def subscriber_count(self) -> int:
        """订阅者总数"""
        return sum(len(handlers) for handlers in self._subscribers.values())
