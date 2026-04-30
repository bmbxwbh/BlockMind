"""BlockMind 核心引擎 — 双 Agent 架构"""

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
from src.ai.main_agent import MainAgent
from src.ai.operation_agent import OperationAgent
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
    BlockMind 主引擎 — 双 Agent 架构

    主 Agent：玩家聊天，指令识别，结果回复（持久上下文）
    操作 Agent：任务执行，Skill 生成/匹配（无状态，用完即弃）
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger("blockmind.engine")
        self.event_bus = EventBus()
        self._running = False

        # ── 通信层 ──
        self.mod_client = ModClient(host="localhost", port=25580)
        self.ws_client = ModWebSocketClient(host="localhost", port=25580, event_bus=self.event_bus)

        # ── 游戏层 ──
        self.state_collector = StateCollector(self.mod_client)
        self.inventory_manager = InventoryManager(self.mod_client)
        self.pathfinder = Pathfinder(self.mod_client)
        self.safety_gateway = SafetyGateway(self.event_bus, config.safety)
        self.action_executor = ActionExecutor(self.mod_client, self.safety_gateway)
        self.action_queue = ActionQueue()
        self.chat_handler = ChatHandler(self.event_bus, self.mod_client)

        # ── Skill 层 ──
        self.skill_storage = SkillStorage(config.skills.storage_path)
        self.skill_matcher = SkillMatcher(self.skill_storage)
        self.skill_runtime = SkillRuntime(
            self.mod_client, self.state_collector,
            self.action_executor, self.state_collector,
        )

        # ── 双 Agent 架构 ──
        main_provider = create_provider(config.ai.get_main_agent())
        op_provider = create_provider(config.ai.get_operation_agent())

        self.main_agent = MainAgent(main_provider)
        self.operation_agent = OperationAgent(op_provider, self.skill_storage)

        # ── 任务分类（兼容旧逻辑）──
        self.task_classifier = TaskClassifier()
        self.task_router = TaskRouter(
            self.task_classifier, self.skill_runtime,
            self.skill_storage, None, self.action_executor,
        )

        # ── 监控层 ──
        self.alerter = Alerter(self.mod_client)
        self.circuit_breaker = CircuitBreaker()
        self.fallback_manager = FallbackManager(self.alerter)
        self.health_checker = HealthChecker(self.mod_client, main_provider)

        # ── 空闲任务 ──
        self.idle_detector = IdleDetector(config.idle_tasks.interval)
        self.task_pool = TaskPool()
        self.idle_scheduler = IdleTaskScheduler(
            self.idle_detector, self.task_pool,
            self.event_bus, self.skill_runtime,
        )

        # ── 紧急接管 ──
        self.emergency_takeover = EmergencyTakeover(op_provider, self.action_executor)

        self.logger.info("✅ CompanionEngine 初始化完成（双 Agent 架构）")

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

        # 注册玩家指令处理（双 Agent 流程）
        self._register_player_command_handler()

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

        await self.event_bus.emit(Event(type="engine.stopped", data={}, source="engine"))

        for module in [self.idle_scheduler, self.health_checker, self.ws_client, self.mod_client]:
            try:
                await module.stop() if hasattr(module, 'stop') else await module.disconnect()
            except Exception:
                pass

        self.logger.info("✅ BlockMind 已安全关闭")

    def _register_player_command_handler(self) -> None:
        """注册玩家指令处理 — 双 Agent 流程

        流程：
        1. 玩家消息 → 主 Agent 聊天
        2. 主 Agent 识别到 [TASK:] → 提取任务描述
        3. 任务描述 → 操作 Agent（无状态）
        4. 操作 Agent 返回结果 → 执行
        5. 主 Agent 格式化回复 → 玩家
        """
        async def on_player_chat(event: Event):
            player = event.data.get("player", "")
            message = event.data.get("message", "")

            if not message or not player:
                return

            # 系统指令优先处理
            if message.startswith("!"):
                return  # 由 ChatHandler 处理

            # 主 Agent 聊天
            result = await self.main_agent.chat(message)

            # 发送聊天回复
            if result["reply"]:
                await self.action_executor.send_chat(result["reply"])

            # 如果识别到任务，派发给操作 Agent
            if result["has_task"] and result["task_description"]:
                await self._dispatch_to_operation_agent(result["task_description"])

        self.event_bus.subscribe("chat", on_player_chat)
        self.logger.info("双 Agent 指令处理已注册")

    async def _dispatch_to_operation_agent(self, task: str) -> None:
        """将任务派发给操作 Agent"""
        try:
            # 获取游戏状态
            status = await self.mod_client.get_status()
            game_state = {
                "health": status.health,
                "hunger": status.hunger,
                "position": status.position,
                "dimension": status.dimension,
                "weather": status.weather,
            }

            # 获取 Skill 元数据
            all_skills = self.skill_storage.list_all()
            skill_metadata = [
                {"name": s.name, "tags": s.tags, "skill_id": s.skill_id}
                for s in all_skills
            ]

            # 操作 Agent 决策（无状态，全新上下文）
            op_result = await self.operation_agent.execute(task, game_state, skill_metadata)

            # 根据策略执行
            strategy = op_result.get("strategy")

            if strategy == "cached_skill" and op_result.get("skill"):
                # 执行缓存 Skill
                result = await self.skill_runtime.execute_skill_object(op_result["skill"])
                reply = await self.main_agent.format_result(op_result)
                await self.action_executor.send_chat(reply)

            elif strategy == "new_skill" and op_result.get("skill"):
                # 执行新生成的 Skill
                result = await self.skill_runtime.execute_skill_object(op_result["skill"])
                reply = await self.main_agent.format_result(op_result)
                await self.action_executor.send_chat(reply)

            elif strategy == "action_sequence" and op_result.get("actions"):
                # 执行动作序列
                results = await self.action_executor.execute_sequence(op_result["actions"])
                reply = await self.main_agent.format_result(op_result)
                await self.action_executor.send_chat(reply)

            else:
                reply = await self.main_agent.format_result(op_result)
                await self.action_executor.send_chat(reply)

        except Exception as e:
            self.logger.error(f"操作 Agent 执行失败: {e}")
            await self.action_executor.send_chat(f"❌ 执行出错: {str(e)[:50]}")

    def _register_commands(self) -> None:
        """注册系统指令"""
        async def handle_stop(cmd):
            count = await self.action_queue.cancel_all()
            await self.chat_handler.send_system_message(f"§e已终止 {count} 个任务")

        async def handle_status(cmd):
            status = await self.mod_client.get_status()
            inv = await self.mod_client.get_inventory()
            skills = self.skill_storage.list_all()
            msg = (
                f"§6§l=== BlockMind 状态 ===\n"
                f"§e生命: §c{status.health:.1f} §e饥饿: §6{status.hunger}\n"
                f"§e位置: §a({status.position.get('x',0):.0f}, {status.position.get('y',0):.0f}, {status.position.get('z',0):.0f})\n"
                f"§e维度: §b{status.dimension} §e天气: §7{status.weather}\n"
                f"§e背包: §a{len(inv.items)} 物品 §7({inv.empty_slots} 空位)\n"
                f"§e技能: §a{len(skills)} 个已缓存"
            )
            await self.chat_handler.send_system_message(msg)

        async def handle_safe(cmd):
            await self.action_executor.send_chat("正在返回安全点...")
            await self.mod_client.move(0, 64, 0)

        self.chat_handler.register_command("stop", handle_stop)
        self.chat_handler.register_command("status", handle_status)
        self.chat_handler.register_command("safe", handle_safe)
        self.chat_handler.register_command("help", lambda cmd: self.chat_handler.send_help())
        self.logger.info("系统指令已注册")
