"""动作队列 — 管理待执行的游戏动作，支持超时、取消、重试"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Callable, Optional, List, Dict, Any
from enum import Enum

logger = logging.getLogger("blockmind.action_queue")


class ActionPriority(Enum):
    """动作优先级"""
    CRITICAL = 0   # 紧急（逃跑、回血）
    HIGH = 1       # 高优（响应玩家指令）
    NORMAL = 2     # 普通（技能执行）
    LOW = 3        # 低优（空闲任务）
    IDLE = 4       # 空闲


class ActionStatus(Enum):
    """动作状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class QueuedAction:
    """队列中的动作"""
    action_id: str
    action_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    priority: ActionPriority = ActionPriority.NORMAL
    timeout: float = 30.0
    max_retries: int = 0
    status: ActionStatus = ActionStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0


class ActionQueue:
    """动作队列

    管理待执行的游戏动作，支持：
    - 优先级排序
    - 超时检测
    - 取消操作
    - 失败重试
    - 并发限制
    """

    def __init__(self, max_concurrent: int = 1):
        self.max_concurrent = max_concurrent
        self._queue: List[QueuedAction] = []
        self._running: Dict[str, QueuedAction] = {}
        self._counter = 0
        self._handlers: Dict[str, Callable] = {}
        self._lock = asyncio.Lock()

    def register_handler(self, action_type: str, handler: Callable) -> None:
        """注册动作处理器"""
        self._handlers[action_type] = handler

    def _next_id(self) -> str:
        self._counter += 1
        return f"act_{self._counter}"

    async def enqueue(
        self,
        action_type: str,
        params: Dict[str, Any] = None,
        priority: ActionPriority = ActionPriority.NORMAL,
        timeout: float = 30.0,
        max_retries: int = 0,
    ) -> str:
        """添加动作到队列，返回 action_id"""
        action = QueuedAction(
            action_id=self._next_id(),
            action_type=action_type,
            params=params or {},
            priority=priority,
            timeout=timeout,
            max_retries=max_retries,
        )
        async with self._lock:
            self._queue.append(action)
            self._queue.sort(key=lambda a: a.priority.value)
        logger.debug(f"入队: {action.action_id} ({action_type}) 优先级={priority.name}")
        return action.action_id

    async def process_next(self) -> Optional[QueuedAction]:
        """处理队列中下一个动作"""
        if len(self._running) >= self.max_concurrent:
            return None

        async with self._lock:
            if not self._queue:
                return None
            action = self._queue.pop(0)
            action.status = ActionStatus.RUNNING
            action.started_at = time.time()
            self._running[action.action_id] = action

        handler = self._handlers.get(action.action_type)
        if handler is None:
            action.status = ActionStatus.FAILED
            action.error = f"未注册的动作类型: {action.action_type}"
            self._running.pop(action.action_id, None)
            return action

        try:
            result = await asyncio.wait_for(
                handler(action.params),
                timeout=action.timeout,
            )
            action.result = result
            action.status = ActionStatus.COMPLETED
        except asyncio.TimeoutError:
            action.status = ActionStatus.TIMEOUT
            action.error = f"动作超时 ({action.timeout}s)"
            logger.warning(f"动作超时: {action.action_id}")
        except Exception as e:
            action.error = str(e)
            if action.retry_count < action.max_retries:
                action.retry_count += 1
                action.status = ActionStatus.PENDING
                async with self._lock:
                    self._queue.insert(0, action)
                logger.info(f"重试动作: {action.action_id} ({action.retry_count}/{action.max_retries})")
            else:
                action.status = ActionStatus.FAILED
                logger.error(f"动作失败: {action.action_id} — {e}")

        action.completed_at = time.time()
        self._running.pop(action.action_id, None)
        return action

    async def cancel(self, action_id: str) -> bool:
        """取消动作"""
        async with self._lock:
            for action in self._queue:
                if action.action_id == action_id:
                    action.status = ActionStatus.CANCELLED
                    self._queue.remove(action)
                    return True
            if action_id in self._running:
                self._running[action_id].status = ActionStatus.CANCELLED
                return True
        return False

    async def cancel_all(self) -> int:
        """取消所有动作，返回取消数量"""
        count = 0
        async with self._lock:
            for action in self._queue:
                action.status = ActionStatus.CANCELLED
                count += 1
            self._queue.clear()
            for action in self._running.values():
                action.status = ActionStatus.CANCELLED
                count += 1
        return count

    @property
    def pending_count(self) -> int:
        return len(self._queue)

    @property
    def running_count(self) -> int:
        return len(self._running)

    @property
    def is_empty(self) -> bool:
        return len(self._queue) == 0 and len(self._running) == 0

    def get_queue_snapshot(self) -> List[Dict]:
        """获取队列快照"""
        return [
            {
                "id": a.action_id,
                "type": a.action_type,
                "priority": a.priority.name,
                "status": a.status.value,
                "retries": a.retry_count,
            }
            for a in self._queue + list(self._running.values())
        ]
