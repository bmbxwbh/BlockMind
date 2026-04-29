"""BlockMind 核心引擎"""
import asyncio
import logging
from src.config.loader import AppConfig
from src.core.event_bus import EventBus, Event


class CompanionEngine:
    """
    BlockMind 主引擎

    职责：
    1. 初始化所有子模块
    2. 启动主循环
    3. 协调模块间通信
    4. 优雅关闭
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger("blockmind.engine")
        self.event_bus = EventBus()
        self._running = False

        # 以下模块将在后续阶段初始化
        self.connection = None       # P1: MCConnection
        self.state_collector = None  # P1: StateCollector
        self.skill_runtime = None    # P2: SkillRuntime
        self.ai_decider = None       # P3: AIDecider
        self.safety_gateway = None   # P4: SafetyGateway
        self.health_checker = None   # P5: HealthChecker
        self.idle_scheduler = None   # P6: IdleTaskScheduler

        self.logger.info("✅ CompanionEngine 初始化完成")

    async def start(self) -> None:
        """启动引擎"""
        self._running = True
        self.logger.info("🚀 BlockMind 引擎启动")

        # 发布启动事件
        await self.event_bus.emit(Event(
            type="engine.started",
            data={"config": self.config.model_dump()},
            source="engine"
        ))

        # 主循环（占位，后续接入各模块）
        while self._running:
            await asyncio.sleep(1)

    async def shutdown(self) -> None:
        """优雅关闭"""
        self.logger.info("🛑 BlockMind 引擎关闭中...")
        self._running = False

        await self.event_bus.emit(Event(
            type="engine.stopped",
            data={},
            source="engine"
        ))

        # 关闭各模块（后续填充）
        if self.connection:
            await self.connection.disconnect()

        self.logger.info("✅ BlockMind 已安全关闭")
