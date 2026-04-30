"""BlockMind 核心引擎 — 双 Agent 架构 + 记忆系统"""

import asyncio
import logging
from typing import Optional

from src.config.loader import AppConfig
from src.core.event_bus import EventBus, Event
from src.core.memory import GameMemory
from src.mod_client.client import ModClient
from src.mod_client.ws_client import ModWebSocketClient
from src.game.perception import StateCollector
from src.game.actions import ActionExecutor
from src.game.action_queue import ActionQueue
from src.game.inventory import InventoryManager
from src.game.chat import ChatHandler
from src.game.pathfinding import Pathfinder
from src.game.navigation import SmartNavigator
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
    BlockMind 主引擎 — 双 Agent + 记忆系统

    架构：
    ┌─────────────────────────────────────────────────┐
    │ 主 Agent（聊天 + 指令识别）                       │
    │ 操作 Agent（无状态任务执行）                      │
    ├─────────────────────────────────────────────────┤
    │ 记忆系统（空间/路径/策略/玩家/世界记忆）          │
    │ 智能导航（记忆驱动 + Baritone 集成）             │
    ├─────────────────────────────────────────────────┤
    │ Skill 引擎（DSL 解析 + 匹配 + 执行）             │
    │ 安全校验 + 健康监控 + 空闲任务                   │
    └─────────────────────────────────────────────────┘
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger("blockmind.engine")
        self.event_bus = EventBus()
        self._running = False

        # ── 通信层 ──
        self.mod_client = ModClient(host="localhost", port=25580)
        self.ws_client = ModWebSocketClient(host="localhost", port=25580, event_bus=self.event_bus)

        # ── 记忆系统（核心新增）──
        self.memory = GameMemory(storage_path=config.memory.storage_path)

        # ── 游戏层 ──
        self.state_collector = StateCollector(self.mod_client)
        self.inventory_manager = InventoryManager(self.mod_client)
        self.pathfinder = Pathfinder(self.mod_client)
        self.safety_gateway = SafetyGateway(self.event_bus, config.safety)
        self.action_executor = ActionExecutor(self.mod_client, self.safety_gateway)
        self.action_queue = ActionQueue()
        self.chat_handler = ChatHandler(self.event_bus, self.mod_client)

        # ── 智能导航（核心新增）──
        self.navigator = SmartNavigator(
            mod_client=self.mod_client,
            memory=self.memory,
            pathfinder=self.pathfinder,
        )

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

        # ── 任务分类 ──
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

        self.logger.info("✅ CompanionEngine 初始化完成（双 Agent + 记忆系统）")

    async def start(self) -> None:
        """启动引擎"""
        self._running = True
        self.logger.info("🚀 BlockMind 引擎启动")

        # 连接 Mod API
        connected = await self.mod_client.connect()
        if connected:
            self.logger.info("✅ Mod API 连接成功")
            await self.ws_client.connect()

            # 初始化世界记忆
            await self._init_world_memory()
        else:
            self.logger.warning("⚠️ Mod API 连接失败，部分功能不可用")

        # 注册系统指令
        self._register_commands()

        # 注册玩家指令处理（双 Agent 流程）
        self._register_player_command_handler()

        # 注册记忆学习事件
        self._register_memory_learning()

        # 启动健康检查
        await self.health_checker.start()

        # 启动空闲任务调度
        if self.config.idle_tasks.enabled:
            await self.idle_scheduler.start()

        # 启动自动环境检测（定时扫描周围区域）
        if self.config.memory.auto_detect_zones:
            asyncio.create_task(self._auto_detect_loop())

        # 发布启动事件
        await self.event_bus.emit(Event(
            type="engine.started",
            data={"config": self.config.model_dump()},
            source="engine",
        ))

        self.logger.info("✅ 所有模块启动完成")
        self.logger.info(f"🧠 记忆统计: {self.memory.get_stats()}")

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

        # 保存记忆
        self.logger.info(f"💾 记忆保存中... {self.memory.get_stats()}")

        await self.event_bus.emit(Event(type="engine.stopped", data={}, source="engine"))

        for module in [self.idle_scheduler, self.health_checker, self.ws_client, self.mod_client]:
            try:
                await module.stop() if hasattr(module, 'stop') else await module.disconnect()
            except Exception:
                pass

        self.logger.info("✅ BlockMind 已安全关闭")

    # ── 双 Agent 指令处理 ────────────────────────────

    def _register_player_command_handler(self) -> None:
        """注册玩家指令处理 — 双 Agent 流程（注入记忆上下文）"""
        async def on_player_chat(event: Event):
            player = event.data.get("player", "")
            message = event.data.get("message", "")

            if not message or not player:
                return

            # 系统指令优先处理
            if message.startswith("!"):
                return

            # 记录玩家交互
            self.memory.record_player_interaction(player)

            # 获取记忆上下文注入到 AI
            memory_context = self.memory.get_ai_context()

            # 主 Agent 聊天（注入记忆）
            result = await self.main_agent.chat(message, context=memory_context)

            # 发送聊天回复
            if result["reply"]:
                await self.action_executor.send_chat(result["reply"])

            # 如果识别到任务，派发给操作 Agent
            if result["has_task"] and result["task_description"]:
                await self._dispatch_to_operation_agent(
                    result["task_description"], player
                )

        self.event_bus.subscribe("chat", on_player_chat)
        self.logger.info("双 Agent 指令处理已注册（含记忆注入）")

    async def _dispatch_to_operation_agent(self, task: str,
                                            player_name: str = "player") -> None:
        """将任务派发给操作 Agent（记忆增强版）"""
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

            # 注入记忆上下文
            memory_context = self.memory.get_ai_context()

            # 操作 Agent 决策（无状态，注入记忆）
            op_result = await self.operation_agent.execute(
                task, game_state, skill_metadata, context=memory_context
            )

            # 根据策略执行
            strategy = op_result.get("strategy")

            if strategy == "cached_skill" and op_result.get("skill"):
                result = await self.skill_runtime.execute_skill_object(op_result["skill"])
                # 记忆学习：记录策略执行结果
                self.memory.record_strategy(
                    task_type="skill_execution",
                    description=f"执行缓存Skill: {op_result['skill'].name}",
                    action_sequence=[{"skill": op_result["skill"].skill_id}],
                    success=result.success if hasattr(result, 'success') else True,
                )
                reply = await self.main_agent.format_result(op_result)
                await self.action_executor.send_chat(reply)

            elif strategy == "new_skill" and op_result.get("skill"):
                result = await self.skill_runtime.execute_skill_object(op_result["skill"])
                self.memory.record_strategy(
                    task_type="skill_execution",
                    description=f"执行新Skill: {op_result['skill'].name}",
                    action_sequence=[{"skill": op_result["skill"].skill_id}],
                    success=result.success if hasattr(result, 'success') else True,
                )
                reply = await self.main_agent.format_result(op_result)
                await self.action_executor.send_chat(reply)

            elif strategy == "action_sequence" and op_result.get("actions"):
                results = await self.action_executor.execute_sequence(op_result["actions"])
                # 记忆学习
                success = all(r.get("result", {}).success for r in results if hasattr(r.get("result", {}), 'success'))
                self.memory.record_strategy(
                    task_type="action_sequence",
                    description=task[:100],
                    action_sequence=op_result["actions"],
                    success=success,
                )
                reply = await self.main_agent.format_result(op_result)
                await self.action_executor.send_chat(reply)

            else:
                reply = await self.main_agent.format_result(op_result)
                await self.action_executor.send_chat(reply)

        except Exception as e:
            self.logger.error(f"操作 Agent 执行失败: {e}")
            await self.action_executor.send_chat(f"❌ 执行出错: {str(e)[:50]}")

    # ── 记忆系统集成 ─────────────────────────────────

    async def _init_world_memory(self) -> None:
        """初始化世界记忆"""
        try:
            status = await self.mod_client.get_status()
            pos = status.position
            position = (int(pos.get("x", 0)), int(pos.get("y", 64)), int(pos.get("z", 0)))

            if not self.memory.world.spawn_point:
                self.memory.set_spawn_point(position)
                self.memory.add_safe_point(position)

            self.logger.info(f"🌍 世界记忆初始化: 出生点={position}")
        except Exception as e:
            self.logger.warning(f"世界记忆初始化失败: {e}")

    def _register_memory_learning(self) -> None:
        """注册记忆学习事件监听"""
        async def on_action_completed(event: Event):
            """动作完成时学习"""
            action = event.data.get("action", "")
            success = event.data.get("success", False)
            duration = event.data.get("duration", 0.0)

            if action in ("navigate", "goto", "walk_to"):
                # 导航完成 → 记录路径
                start = event.data.get("start")
                end = event.data.get("end")
                waypoints = event.data.get("waypoints", [])
                if start and end:
                    self.memory.cache_path(
                        tuple(start), tuple(end), waypoints,
                        success=success, duration=duration,
                    )

        self.event_bus.subscribe("action.completed", on_action_completed)
        self.logger.info("📝 记忆学习事件已注册")

    async def _auto_detect_loop(self) -> None:
        """定时自动检测环境（后台任务）"""
        while self._running:
            try:
                await asyncio.sleep(60)  # 每60秒扫描一次
                if self._running:
                    await self.navigator.auto_detect_and_memorize()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.warning(f"自动环境检测异常: {e}")
                await asyncio.sleep(10)

    # ── 系统指令 ─────────────────────────────────────

    def _register_commands(self) -> None:
        """注册系统指令（增加记忆相关指令）"""
        async def handle_stop(cmd):
            count = await self.action_queue.cancel_all()
            await self.chat_handler.send_system_message(f"§e已终止 {count} 个任务")

        async def handle_status(cmd):
            status = await self.mod_client.get_status()
            inv = await self.mod_client.get_inventory()
            skills = self.skill_storage.list_all()
            mem_stats = self.memory.get_stats()
            msg = (
                f"§6§l=== BlockMind 状态 ===\n"
                f"§e生命: §c{status.health:.1f} §e饥饿: §6{status.hunger}\n"
                f"§e位置: §a({status.position.get('x',0):.0f}, {status.position.get('y',0):.0f}, {status.position.get('z',0):.0f})\n"
                f"§e维度: §b{status.dimension} §e天气: §7{status.weather}\n"
                f"§e背包: §a{len(inv.items)} 物品 §7({inv.empty_slots} 空位)\n"
                f"§e技能: §a{len(skills)} 个已缓存\n"
                f"§e记忆: §a{mem_stats['zones']} 区域 §7| §a{mem_stats['cached_paths']} 路径 §7| §a{mem_stats['strategies']} 策略"
            )
            await self.chat_handler.send_system_message(msg)

        async def handle_memory(cmd):
            """!memory — 显示记忆系统详情"""
            stats = self.memory.get_stats()
            zones = self.memory.zones
            msg = f"§6§l=== 记忆系统 ===\n"
            msg += f"§e区域: §a{stats['zones']} §7(保护区 {stats['protected_zones']})\n"
            msg += f"§e路径: §a{stats['cached_paths']} §7(可靠 {stats['reliable_paths']})\n"
            msg += f"§e策略: §a{stats['strategies']}\n"
            msg += f"§e玩家: §a{stats['players']} §e事件: §a{stats['events']}\n"
            if zones:
                msg += "§e--- 区域列表 ---\n"
                for z in list(zones.values())[:10]:
                    msg += f"§7  [{z.zone_type.value}] §f{z.name} §7@ {z.center}\n"
            await self.chat_handler.send_system_message(msg)

        async def handle_safe(cmd):
            """前往最近的安全点"""
            await self.action_executor.send_chat("正在前往安全点...")
            result = await self.navigator.go_to_safe_point()
            if result.success:
                await self.action_executor.send_chat(f"§a已到达安全点 ({result.duration:.1f}s)")
            else:
                await self.action_executor.send_chat(f"§c无法到达安全点: {result.message}")

        self.chat_handler.register_command("stop", handle_stop)
        self.chat_handler.register_command("status", handle_status)
        self.chat_handler.register_command("memory", handle_memory)
        self.chat_handler.register_command("safe", handle_safe)
        self.chat_handler.register_command("help", lambda cmd: self.chat_handler.send_help())
        self.logger.info("系统指令已注册（含记忆指令）")
