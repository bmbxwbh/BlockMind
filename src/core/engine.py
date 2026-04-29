"""BlockMind 核心引擎 — 集成所有模块的主引擎"""

import asyncio
import logging
from typing import Optional

from src.config.loader import AppConfig
from src.core.event_bus import EventBus, Event
from src.mod_client.client import ModClient
from src.mod_client.ws_client import ModWebSocketClient
from src.game.perception import StateCollector
from src.game.actions import ActionExecutor
from src.game.action_queue import ActionQueue
from src.game.inventory import InventoryManager
from src.game.chat import ChatHandler
from src.game.pathfinding import Pathfinder
from src.skills.runtime import SkillRuntime
from src.skills.storage import SkillStorage
from src.skills.matcher import SkillMatcher
from src.ai.provider import create_provider
from src.ai.generator import DSLGenerator
from src.ai.takeover import EmergencyTakeover
from src.safety.gateway import SafetyGateway
from src.monitoring.health import HealthChecker
from src.monitoring.fallback import FallbackManager
from src.monitoring.alerter import Alerter
from src.monitoring.circuit_breaker import CircuitBreaker
from src.core.task_classifier import TaskClassifier
from src.core.task_router import TaskRouter
from src.core.idle_detector import IdleDetector
from src.core.task_pool import TaskPool
from src.core.idle_scheduler import IdleTaskScheduler


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

        # ── 通信层 ──
        self.mod_client = ModClient(
            host="localhost",
            port=25580,
        )
        self.ws_client = ModWebSocketClient(
            host="localhost",
            port=25580,
            event_bus=self.event_bus,
        )

        # ── 游戏层 ──
        self.state_collector = StateCollector(self.mod_client)
        self.inventory_manager = InventoryManager(self.mod_client)
        self.pathfinder = Pathfinder(self.mod_client)
        self.safety_gateway = SafetyGateway(self.event_bus, config.safety)
        self.action_executor = ActionExecutor(self.mod_client, self.safety_gateway)
        self.action_queue = ActionQueue()
        self.chat_handler = ChatHandler(self.event_bus, self.mod_client)

        # ── AI 层 ──
        self.ai_provider = create_provider(config.ai)
        self.dsl_generator = DSLGenerator(self.ai_provider)

        # ── Skill 层 ──
        self.skill_storage = SkillStorage(config.skills.storage_path)
        self.skill_matcher = SkillMatcher(self.skill_storage)
        self.skill_runtime = SkillRuntime(
            self.mod_client, self.state_collector,
            self.action_executor, self.state_collector,
        )

        # ── 任务分类 ──
        self.task_classifier = TaskClassifier()
        self.task_router = TaskRouter(
            self.task_classifier, self.skill_runtime,
            self.skill_storage, self.dsl_generator,
            self.action_executor,
        )

        # ── 监控层 ──
        self.alerter = Alerter(self.mod_client)
        self.circuit_breaker = CircuitBreaker()
        self.fallback_manager = FallbackManager(self.alerter)
        self.health_checker = HealthChecker(self.mod_client, self.ai_provider)

        # ── 空闲任务 ──
        self.idle_detector = IdleDetector(config.idle_tasks.interval)
        self.task_pool = TaskPool()
        self.idle_scheduler = IdleTaskScheduler(
            self.idle_detector, self.task_pool,
            self.event_bus, self.skill_runtime,
        )

        # ── 紧急接管 ──
        self.emergency_takeover = EmergencyTakeover(
            self.ai_provider, self.action_executor,
        )

        self.logger.info("✅ CompanionEngine 初始化完成")

    async def start(self) -> None:
        """启动引擎"""
        self._running = True
        self.logger.info("🚀 BlockMind 引擎启动")

        # 连接 Mod API
        connected = await self.mod_client.connect()
        if connected:
            self.logger.info("✅ Mod API 连接成功")
            await self.ws_client.connect()
        else:
            self.logger.warning("⚠️ Mod API 连接失败，部分功能不可用")

        # 注册聊天指令
        self._register_commands()

        # 启动健康检查
        await self.health_checker.start()

        # 启动空闲任务调度
        if self.config.idle_tasks.enabled:
            await self.idle_scheduler.start()

        # 发布启动事件
        await self.event_bus.emit(Event(
            type="engine.started",
            data={"config": self.config.model_dump()},
            source="engine",
        ))

        self.logger.info("✅ 所有模块启动完成")

        # 主循环
        while self._running:
            try:
                # 处理动作队列
                if not self.action_queue.is_empty:
                    await self.action_queue.process_next()
                await asyncio.sleep(0.1)
            except Exception as e:
                self.logger.error(f"主循环异常: {e}")
                await asyncio.sleep(1)

    async def shutdown(self) -> None:
        """优雅关闭"""
        self.logger.info("🛑 BlockMind 引擎关闭中...")
        self._running = False

        await self.event_bus.emit(Event(
            type="engine.stopped",
            data={},
            source="engine",
        ))

        # 按依赖逆序关闭
        try:
            await self.idle_scheduler.stop()
        except Exception:
            pass
        try:
            await self.health_checker.stop()
        except Exception:
            pass
        try:
            await self.ws_client.disconnect()
        except Exception:
            pass
        try:
            await self.mod_client.disconnect()
        except Exception:
            pass

        self.logger.info("✅ BlockMind 已安全关闭")

    def _register_commands(self) -> None:
        """注册聊天指令处理器"""
        async def handle_stop(cmd):
            count = await self.action_queue.cancel_all()
            await self.chat_handler.send_system_message(f"§e已终止 {count} 个任务")

        async def handle_status(cmd):
            status = await self.mod_client.get_status()
            inv = await self.mod_client.get_inventory()
            msg = (
                f"§6§l=== BlockMind 状态 ===\n"
                f"§e生命: §c{status.health:.1f} §e饥饿: §6{status.hunger}\n"
                f"§e位置: §a({status.position.get('x',0):.0f}, {status.position.get('y',0):.0f}, {status.position.get('z',0):.0f})\n"
                f"§e维度: §b{status.dimension} §e天气: §7{status.weather}\n"
                f"§e背包: §a{len(inv.items)} 物品 §7({inv.empty_slots} 空位)"
            )
            await self.chat_handler.send_system_message(msg)

        async def handle_safe(cmd):
            # 回到安全点（家的位置或世界出生点）
            await self.action_executor.send_chat("正在返回安全点...")
            await self.mod_client.move(0, 64, 0)

        self.chat_handler.register_command("stop", handle_stop)
        self.chat_handler.register_command("status", handle_status)
        self.chat_handler.register_command("safe", handle_safe)
        self.chat_handler.register_command("help", lambda cmd: self.chat_handler.send_help())

        self.logger.info("聊天指令已注册")
