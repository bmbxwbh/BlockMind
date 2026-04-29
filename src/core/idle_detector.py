"""空闲检测器 — 判断是否进入空闲模式"""
import time
import logging


class IdleDetector:
    """空闲检测器

    空闲条件（同时满足）：
    1. 无玩家指令（最近 N 秒内无 ! 指令）
    2. 无危险（附近无敌对生物，血量 > 50%）
    3. 无待执行任务（当前任务队列为空）
    """

    def __init__(self, idle_threshold: int = 30):
        self.idle_threshold = idle_threshold  # 空闲判定阈值（秒）
        self._last_command_time = time.time()
        self._has_pending_tasks = False
        self.logger = logging.getLogger("blockmind.idle_detector")

    def on_command_received(self) -> None:
        """收到玩家指令时调用"""
        self._last_command_time = time.time()

    def set_pending_tasks(self, has_tasks: bool) -> None:
        """设置是否有待执行任务"""
        self._has_pending_tasks = has_tasks

    def is_idle(self, health: float = 20.0, hostile_nearby: bool = False) -> bool:
        """判断是否空闲"""
        # 条件1：无玩家指令
        time_since_command = time.time() - self._last_command_time
        if time_since_command < self.idle_threshold:
            return False

        # 条件2：无危险
        if hostile_nearby:
            return False
        if health < 10:  # 血量低于 50%
            return False

        # 条件3：无待执行任务
        if self._has_pending_tasks:
            return False

        return True
