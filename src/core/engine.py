"""BlockMind 核心引擎 — 双 Agent 架构 + 记忆系统"""

import asyncio
import json
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
from src.game.dynmap_client import DynmapClient
from src.skills.runtime import SkillRuntime
from src.skills.storage import SkillStorage
from src.skills.matcher import SkillMatcher
from src.ai.provider import create_provider
from src.ai.token_tracker import TokenTracker
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
        mod_cfg = config.mod
        self._no_mod_mode = mod_cfg.no_mod_mode
        self.mod_client = ModClient(
            host=mod_cfg.host,
            port=mod_cfg.port,
            timeout=mod_cfg.timeout,
        )
        self.ws_client = ModWebSocketClient(
            host=mod_cfg.host,
            port=mod_cfg.port,
            event_bus=self.event_bus,
            initial_backoff=mod_cfg.ws_backoff.initial_backoff,
            max_backoff=mod_cfg.ws_backoff.max_backoff,
            backoff_multiplier=mod_cfg.ws_backoff.backoff_multiplier,
        )

        # ── 记忆系统（核心新增）──
        self.memory = GameMemory(storage_path=config.memory.storage_path)

        # ── Dynmap 集成（可选）──
        self.dynmap: Optional[DynmapClient] = None
        self._dynmap_update_task: Optional[asyncio.Task] = None

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

        # ── Token 使用统计 ──
        self.main_provider = main_provider
        self.op_provider = op_provider

        self.main_agent = MainAgent(main_provider)
        self.operation_agent = OperationAgent(op_provider, self.skill_storage, self.skill_matcher)

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
            skill_storage=self.skill_storage,
        )

        # ── 紧急接管 ──
        self.emergency_takeover = EmergencyTakeover(op_provider, self.action_executor)

        self.logger.info("✅ CompanionEngine 初始化完成（双 Agent + 记忆系统）")

    async def start(self) -> None:
        """启动引擎"""
        self._running = True
        self.logger.info("🚀 BlockMind 引擎启动")

        # Check if no-mod mode is enabled
        if self._no_mod_mode:
            self.logger.info("🔧 no_mod_mode 已启用，跳过 Mod 连接")
            self.logger.info("   部分功能（状态查询、动作执行、实时事件）将不可用")
        else:
            # 连接 Mod API
            connected = await self.mod_client.connect()
            if connected:
                self.logger.info("✅ Mod API 连接成功")

                # 生成 Bot（FakePlayer）
                bot_name = self.config.mod.bot_name or "BlockMind_Bot"
                spawn_result = await self.mod_client.spawn_bot(bot_name)
                if spawn_result.get("success"):
                    pos = spawn_result.get("position", {})
                    self.logger.info(
                        f"🤖 Bot '{bot_name}' 已加入游戏 @ "
                        f"({pos.get('x', 0)}, {pos.get('y', 0)}, {pos.get('z', 0)})"
                    )
                else:
                    self.logger.warning(f"⚠️ Bot 生成失败: {spawn_result.get('error', 'unknown')}")

                await self.ws_client.connect()

                # 检查 Mod 版本兼容性
                version_info = await self.mod_client.get_mod_version_info()
                if version_info["match"] is False:
                    self.logger.warning(
                        f"⚠️ Mod 版本不兼容: 检测到 {version_info['detected']}，"
                        f"期望 {version_info['expected']}"
                    )

                # 初始化世界记忆
                await self._init_world_memory()

                # 初始化 Dynmap 集成
                self._init_dynmap()
                await self._start_dynmap_updates()
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

        # 取消 Dynmap 更新任务
        if self._dynmap_update_task and not self._dynmap_update_task.done():
            self._dynmap_update_task.cancel()
            try:
                await self._dynmap_update_task
            except asyncio.CancelledError:
                pass

        await self.event_bus.emit(Event(type="engine.stopped", data={}, source="engine"))

        for module in [self.idle_scheduler, self.health_checker, self.ws_client]:
            try:
                await module.stop() if hasattr(module, 'stop') else await module.disconnect()
            except Exception:
                pass

        # 关闭 ModClient（会自动 despawn bot）
        try:
            await self.mod_client.disconnect()
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

            # 通知空闲检测器有玩家活动
            self.idle_detector.on_command_received()

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
                    result["task_description"], player, memory_context
                )

        self.event_bus.subscribe("chat", on_player_chat)
        self.logger.info("双 Agent 指令处理已注册（含记忆注入）")

    def _derive_task_type(self, task: str) -> str:
        """从任务描述推导任务类型"""
        keywords = {
            "挖": "mining", "mine": "mining", "dig": "mining",
            "砍": "chopping", "chop": "chopping", "wood": "chopping",
            "种": "farming", "farm": "farming", "plant": "farming",
            "建": "building", "build": "building",
            "杀": "combat", "kill": "combat", "attack": "combat",
            "吃": "survival", "eat": "survival",
            "找": "exploring", "find": "exploring", "explore": "exploring",
            "存": "storage", "store": "storage", "deposit": "storage",
        }
        task_lower = task.lower()
        for kw, task_type in keywords.items():
            if kw in task_lower:
                return task_type
        return "general"

    async def _dispatch_to_operation_agent(self, task: str,
                                            player_name: str = "player",
                                            memory_context: str = "") -> None:
        """将任务派发给操作 Agent（记忆增强版）"""
        try:
            # 获取游戏状态
            status = await self.mod_client.get_status()
            inv = await self.mod_client.get_inventory()
            inv_summary = f"{len(inv.items)}物品/{inv.empty_slots}空位"
            game_state = {
                "health": status.health,
                "hunger": status.hunger,
                "position": status.position,
                "dimension": status.dimension,
                "weather": status.weather,
                "inventory_summary": inv_summary,
            }

            # 获取 Skill 元数据
            all_skills = self.skill_storage.list_all()
            skill_metadata = [
                {"name": s.name, "tags": s.tags, "skill_id": s.skill_id}
                for s in all_skills
            ]

            # 注入历史最佳策略
            best_strategy = self.memory.get_best_strategy(self._derive_task_type(task))
            strategy_hint = ""
            if best_strategy:
                strategy_hint = f"\n[历史最佳策略] {best_strategy.description} (成功率{best_strategy.success_rate:.0%})"
                if best_strategy.action_sequence:
                    strategy_hint += f"\n历史动作: {json.dumps(best_strategy.action_sequence[:5])}"

            op_context = memory_context + strategy_hint

            # 操作 Agent 决策（无状态，注入记忆）
            op_result = await self.operation_agent.execute(
                task, game_state, skill_metadata, context=op_context
            )

            # 根据策略执行
            strategy = op_result.get("strategy")
            derived_type = self._derive_task_type(task)
            success = False

            if strategy == "cached_skill" and op_result.get("skill"):
                result = await self.skill_runtime.execute_skill_object(op_result["skill"])
                success = result.success if hasattr(result, 'success') else True
                self.memory.record_strategy(
                    task_type=derived_type,
                    description=f"执行缓存Skill: {op_result['skill'].name}",
                    action_sequence=[{"skill": op_result["skill"].skill_id}],
                    success=success,
                )
                skill_id = op_result.get("skill_id")
                if skill_id:
                    self.skill_storage.update_stats(skill_id, success=success)
                reply = await self.main_agent.format_result(op_result)
                await self.action_executor.send_chat(reply)

            elif strategy == "new_skill" and op_result.get("skill"):
                result = await self.skill_runtime.execute_skill_object(op_result["skill"])
                success = result.success if hasattr(result, 'success') else True
                self.memory.record_strategy(
                    task_type=derived_type,
                    description=f"执行新Skill: {op_result['skill'].name}",
                    action_sequence=[{"skill": op_result["skill"].skill_id}],
                    success=success,
                )
                skill_id = op_result.get("skill_id")
                if skill_id:
                    self.skill_storage.update_stats(skill_id, success=success)
                reply = await self.main_agent.format_result(op_result)
                await self.action_executor.send_chat(reply)

            elif strategy == "action_sequence" and op_result.get("actions"):
                results = await self.action_executor.execute_sequence(op_result["actions"])
                success = all(r.get("result", {}).success for r in results if hasattr(r.get("result", {}), 'success'))
                self.memory.record_strategy(
                    task_type=derived_type,
                    description=task[:100],
                    action_sequence=op_result["actions"],
                    success=success,
                )
                reply = await self.main_agent.format_result(op_result)
                await self.action_executor.send_chat(reply)

            else:
                success = False
                reply = await self.main_agent.format_result(op_result)
                await self.action_executor.send_chat(reply)

            # 反馈到主 Agent 历史（支持多轮推理）
            self.main_agent._history.append({
                "role": "system",
                "content": f"[执行结果] 任务'{task}' {'成功' if success else '失败'}"
            })

        except Exception as e:
            self.logger.error(f"操作 Agent 执行失败: {e}")
            await self.action_executor.send_chat(f"❌ 执行出错: {str(e)[:50]}")
            self.main_agent._history.append({
                "role": "system",
                "content": f"[执行结果] 任务'{task}' 异常: {str(e)[:100]}"
            })

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
                    self.memory.check_stale_skills(self.skill_storage)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.warning(f"自动环境检测异常: {e}")
                await asyncio.sleep(10)

    # ── Dynmap 集成（可选）──────────────────────────

    def _init_dynmap(self) -> None:
        """初始化 Dynmap 客户端（如果配置启用）"""
        dynmap_cfg = self.config.dynmap
        if not dynmap_cfg.enabled:
            self.logger.info("🗺️ Dynmap 集成未启用（设置 dynmap.enabled=true 启用）")
            return

        self.dynmap = DynmapClient(
            host=dynmap_cfg.host,
            port=dynmap_cfg.port,
            api_key=dynmap_cfg.api_key,
        )
        self.logger.info(
            f"🗺️ Dynmap 客户端初始化: {dynmap_cfg.host}:{dynmap_cfg.port}"
        )

    async def _start_dynmap_updates(self) -> None:
        """启动 Dynmap 位置定期更新任务"""
        if not self.dynmap:
            return

        # 注册区域同步回调
        self.memory.register_zone_added_callback(self._on_zone_registered)

        connected = await self.dynmap.check_connection()
        if connected:
            self.logger.info("🗺️ Dynmap 连接成功，开始同步标记")
            if self.config.dynmap.sync_zones:
                await self._sync_zones_to_dynmap()
        else:
            self.logger.warning("🗺️ Dynmap 不可达，位置更新将跳过直到连接恢复")

        self._dynmap_update_task = asyncio.create_task(self._dynmap_update_loop())

    async def _dynmap_update_loop(self) -> None:
        """定期更新 Dynmap 上的 bot 位置"""
        while self._running and self.dynmap:
            try:
                interval = self.config.dynmap.update_interval
                await asyncio.sleep(interval)
                if not self._running or not self.dynmap:
                    break

                if self._no_mod_mode:
                    continue

                try:
                    status = await self.mod_client.get_status()
                    pos = status.position
                    world = status.dimension or "world"

                    bot_name = self.config.mod.bot_name or "BlockMind_Bot"
                    await self.dynmap.update_bot_position(
                        bot_name, world,
                        pos.get("x", 0), pos.get("y", 0), pos.get("z", 0),
                    )
                except Exception as e:
                    self.logger.debug(f"Dynmap 位置更新失败: {e}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.debug(f"Dynmap 更新循环异常: {e}")
                await asyncio.sleep(5)

    async def _sync_zones_to_dynmap(self) -> None:
        """将记忆系统中的区域同步到 Dynmap 标记"""
        if not self.dynmap:
            return

        connected = await self.dynmap.check_connection()
        if not connected:
            return

        zone_type_map = {
            "building": "protect",
            "base": "protect",
            "danger": "danger",
            "resource": "resource",
            "farm": "resource",
            "mine": "resource",
        }

        for zone in self.memory.zones.values():
            zone_type = zone.zone_type.value
            marker_type = zone_type_map.get(zone_type, "info")
            cx, cy, cz = zone.center

            if not self._no_mod_mode:
                try:
                    status = await self.mod_client.get_status()
                    world = status.dimension or "world"
                except Exception:
                    world = "world"
            else:
                world = "world"

            await self.dynmap.add_zone_marker(
                zone_name=zone.name,
                world=world,
                x=cx, y=cy, z=cz,
                zone_type=marker_type,
            )

        self.logger.info(f"🗺️ 已同步 {len(self.memory.zones)} 个区域到 Dynmap")

    async def _on_zone_registered(self, zone) -> None:
        """区域注册时的回调 — 同步到 Dynmap"""
        if not self.dynmap:
            return

        connected = await self.dynmap.check_connection()
        if not connected:
            return

        zone_type_map = {
            "building": "protect",
            "base": "protect",
            "danger": "danger",
            "resource": "resource",
            "farm": "resource",
            "mine": "resource",
        }
        marker_type = zone_type_map.get(zone.zone_type.value, "info")
        cx, cy, cz = zone.center

        world = "world"
        if not self._no_mod_mode:
            try:
                status = await self.mod_client.get_status()
                world = status.dimension or "world"
            except Exception:
                pass

        await self.dynmap.add_zone_marker(
            zone_name=zone.name,
            world=world,
            x=cx, y=cy, z=cz,
            zone_type=marker_type,
        )

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
