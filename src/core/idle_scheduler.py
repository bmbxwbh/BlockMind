"""空闲任务调度器"""
import asyncio
import logging
from typing import Optional
from src.core.idle_detector import IdleDetector
from src.core.task_pool import TaskPool, IdleTask
from src.core.event_bus import EventBus, Event


class IdleTaskScheduler:
    """空闲任务调度器

    调度逻辑：
    1. 检测是否空闲
    2. 从任务池选择任务
    3. 执行任务
    4. 休息 N 秒
    5. 循环
    """

    def __init__(self, idle_detector: IdleDetector, task_pool: TaskPool,
                 event_bus: EventBus, skill_runtime=None,
                 interval: int = 30):
        self.idle_detector = idle_detector
        self.task_pool = task_pool
        self.event_bus = event_bus
        self.skill_runtime = skill_runtime
        self.interval = interval
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger("blockmind.idle_scheduler")

    async def start(self) -> None:
        """启动调度器"""
        self._running = True
        self._task = asyncio.create_task(self._schedule_loop())
        self.logger.info("🤖 空闲任务调度器启动")

    async def stop(self) -> None:
        """停止调度器"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.logger.info("⏹️ 空闲任务调度器停止")

    async def _schedule_loop(self) -> None:
        """主调度循环"""
        while self._running:
            try:
                # 检测空闲（需要外部传入游戏状态）
                if self.idle_detector.is_idle():
                    task = self.task_pool.get_next_task()
                    if task:
                        await self._execute_idle_task(task)
                        await asyncio.sleep(self.interval)
                    else:
                        await asyncio.sleep(5)
                else:
                    await asyncio.sleep(5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"调度异常: {e}")
                await asyncio.sleep(5)

    async def _execute_idle_task(self, task: IdleTask) -> None:
        """执行空闲任务"""
        self.logger.info(f"🤖 选择空闲任务: {task.name}")

        await self.event_bus.emit(Event(
            type="idle.started",
            data={"task": task.name, "skill_id": task.skill_id},
            source="idle_scheduler",
        ))

        try:
            if self.skill_runtime and task.skill_id:
                result = await self.skill_runtime.execute_skill(task.skill_id)
                status = "success" if result.success else "failed"
                self.logger.info(f"{'✅' if result.success else '❌'} 空闲任务 {task.name}: {result.details}")
            else:
                self.logger.info(f"⏭️ 跳过任务 {task.name}（无 Skill 引擎）")
                status = "skipped"
        except Exception as e:
            self.logger.error(f"空闲任务执行失败: {e}")
            status = "error"

        await self.event_bus.emit(Event(
            type="idle.ended",
            data={"task": task.name, "status": status},
            source="idle_scheduler",
        ))
