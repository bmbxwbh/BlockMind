"""Mod 通信客户端测试"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from src.mod_client.models import (
    PlayerStatus, WorldState, InventoryState, InventoryItem,
    EntityInfo, BlockInfo, ActionResult, WSMessage,
)


# ── 模型测试 ──

class TestModels:
    """数据模型测试"""

    def test_player_status_from_dict(self):
        data = {
            "connected": True, "health": 18.5, "hunger": 15,
            "position": {"x": 128.5, "y": 64.0, "z": -256.3},
            "rotation": {"yaw": 45.2, "pitch": -12.5},
            "experience": 127, "level": 5,
            "dimension": "overworld", "time_of_day": 6000, "weather": "clear",
        }
        ps = PlayerStatus.from_dict(data)
        assert ps.connected is True
        assert ps.health == 18.5
        assert ps.hunger == 15
        assert ps.position["x"] == 128.5
        assert ps.dimension == "overworld"

    def test_player_status_defaults(self):
        ps = PlayerStatus()
        assert ps.connected is False
        assert ps.health == 20.0
        assert ps.dimension == "overworld"

    def test_world_state_from_dict(self):
        data = {"dimension": "nether", "time_of_day": 13000, "weather": "rain", "difficulty": "hard", "day_count": 100}
        ws = WorldState.from_dict(data)
        assert ws.dimension == "nether"
        assert ws.difficulty == "hard"

    def test_inventory_state_from_dict(self):
        data = {
            "items": [
                {"name": "diamond_sword", "slot": 0, "count": 1, "durability": 1561, "max_durability": 1561},
                {"name": "bread", "slot": 1, "count": 32, "durability": 0, "max_durability": 0},
            ],
            "empty_slots": 34, "is_full": False,
        }
        inv = InventoryState.from_dict(data)
        assert len(inv.items) == 2
        assert inv.count_item("bread") == 32
        assert inv.has_item("bread", 10) is True
        assert inv.has_item("diamond", 1) is False
        assert inv.is_full is False

    def test_entity_info_from_dict(self):
        data = {"id": 123, "type": "zombie", "position": {"x": 130, "y": 64, "z": -258}, "health": 20.0, "hostile": True}
        ei = EntityInfo.from_dict(data)
        assert ei.type == "zombie"
        assert ei.hostile is True

    def test_action_result_from_dict(self):
        data = {"success": True, "details": "移动完成"}
        ar = ActionResult.from_dict(data)
        assert ar.success is True
        assert ar.details == "移动完成"

    def test_action_result_failure(self):
        data = {"success": False, "error": "目标不可达"}
        ar = ActionResult.from_dict(data)
        assert ar.success is False
        assert ar.error == "目标不可达"

    def test_ws_message_from_dict(self):
        data = {"type": "chat", "data": {"player": "Steve", "message": "hi"}}
        ws = WSMessage.from_dict(data)
        assert ws.type == "chat"
        assert ws.data["player"] == "Steve"


# ── ModClient 测试 ──

class TestModClient:
    """ModClient 单元测试（mock HTTP）"""

    @pytest.fixture
    def client(self):
        from src.mod_client.client import ModClient
        return ModClient(host="localhost", port=25580)

    def test_init(self, client):
        assert client.base_url == "http://localhost:25580"
        assert client.is_connected is False

    def test_properties(self, client):
        assert client.is_connected is False


# ── 任务分类器测试 ──

class TestTaskClassifier:
    """任务分类器测试"""

    @pytest.fixture
    def classifier(self):
        from src.core.task_classifier import TaskClassifier
        return TaskClassifier()

    def test_l1_fixed_tasks(self, classifier):
        from src.core.task_classifier import TaskLevel
        assert classifier.classify("吃东西") == TaskLevel.L1_FIXED
        assert classifier.classify("进食") == TaskLevel.L1_FIXED
        assert classifier.classify("整理箱子") == TaskLevel.L1_FIXED
        assert classifier.classify("睡觉") == TaskLevel.L1_FIXED
        assert classifier.classify("回家") == TaskLevel.L1_FIXED

    def test_l2_parameterized_tasks(self, classifier):
        from src.core.task_classifier import TaskLevel
        assert classifier.classify("砍树") == TaskLevel.L2_PARAMETER
        assert classifier.classify("挖矿") == TaskLevel.L2_PARAMETER
        assert classifier.classify("种田") == TaskLevel.L2_PARAMETER
        assert classifier.classify("钓鱼") == TaskLevel.L2_PARAMETER

    def test_l3_template_tasks(self, classifier):
        from src.core.task_classifier import TaskLevel
        assert classifier.classify("建墙") == TaskLevel.L3_TEMPLATE
        assert classifier.classify("铺路") == TaskLevel.L3_TEMPLATE

    def test_l4_dynamic_tasks(self, classifier):
        from src.core.task_classifier import TaskLevel
        assert classifier.classify("建房子") == TaskLevel.L4_DYNAMIC
        assert classifier.classify("探索洞穴") == TaskLevel.L4_DYNAMIC

    def test_unknown_defaults_to_dynamic(self, classifier):
        from src.core.task_classifier import TaskLevel
        assert classifier.classify("随便干点啥") == TaskLevel.L4_DYNAMIC

    def test_get_task_skill_id(self, classifier):
        assert classifier.get_task_skill_id("砍树") == "chop_tree"
        assert classifier.get_task_skill_id("吃东西") == "eat_food"
        assert classifier.get_task_skill_id("未知任务") is None


# ── 事件总线测试 ──

class TestEventBus:
    """事件总线测试"""

    @pytest.fixture
    def bus(self):
        from src.core.event_bus import EventBus
        return EventBus()

    @pytest.mark.asyncio
    async def test_subscribe_and_emit(self, bus):
        from src.core.event_bus import Event
        received = []
        bus.subscribe("test", lambda e: received.append(e))
        event = Event(type="test", data={"key": "value"}, source="test")
        await bus.emit(event)
        assert len(received) == 1
        assert received[0].data["key"] == "value"

    @pytest.mark.asyncio
    async def test_unsubscribe(self, bus):
        from src.core.event_bus import Event
        received = []
        handler = lambda e: received.append(e)
        bus.subscribe("test", handler)
        bus.unsubscribe("test", handler)
        await bus.emit(Event(type="test", data={}, source="test"))
        assert len(received) == 0

    def test_history(self, bus):
        history = bus.get_history()
        assert isinstance(history, list)


# ── 动作队列测试 ──

class TestActionQueue:
    """动作队列测试"""

    @pytest.fixture
    def queue(self):
        from src.game.action_queue import ActionQueue
        return ActionQueue()

    def test_init(self, queue):
        assert queue.is_empty is True
        assert queue.pending_count == 0

    @pytest.mark.asyncio
    async def test_enqueue(self, queue):
        act_id = await queue.enqueue("move", {"x": 1, "y": 2, "z": 3})
        assert act_id is not None
        assert queue.pending_count == 1

    @pytest.mark.asyncio
    async def test_priority_ordering(self, queue):
        from src.game.action_queue import ActionPriority
        await queue.enqueue("low", priority=ActionPriority.LOW)
        await queue.enqueue("critical", priority=ActionPriority.CRITICAL)
        await queue.enqueue("normal", priority=ActionPriority.NORMAL)
        snapshot = queue.get_queue_snapshot()
        assert snapshot[0]["type"] == "critical"
        assert snapshot[1]["type"] == "normal"
        assert snapshot[2]["type"] == "low"

    @pytest.mark.asyncio
    async def test_cancel(self, queue):
        act_id = await queue.enqueue("test")
        result = await queue.cancel(act_id)
        assert result is True
        assert queue.is_empty is True

    @pytest.mark.asyncio
    async def test_cancel_all(self, queue):
        await queue.enqueue("a")
        await queue.enqueue("b")
        count = await queue.cancel_all()
        assert count == 2
        assert queue.is_empty is True


# ── 聊天处理器测试 ──

class TestChatHandler:
    """聊天处理器测试"""

    def test_parse_command(self):
        from src.game.chat import ChatHandler
        handler = ChatHandler.__new__(ChatHandler)
        cmd = handler.parse_command("!stop", "Steve")
        assert cmd is not None
        assert cmd.command == "stop"
        assert cmd.player == "Steve"

    def test_parse_command_with_args(self):
        from src.game.chat import ChatHandler
        handler = ChatHandler.__new__(ChatHandler)
        cmd = handler.parse_command("!come Steve", "Alex")
        assert cmd.command == "come"
        assert cmd.args == "Steve"

    def test_parse_non_command(self):
        from src.game.chat import ChatHandler
        handler = ChatHandler.__new__(ChatHandler)
        cmd = handler.parse_command("hello world", "Steve")
        assert cmd is None


# ── 背包管理器测试 ──

class TestInventoryManager:
    """背包管理器测试"""

    def test_empty_inventory(self):
        from src.game.inventory import InventoryManager
        mgr = InventoryManager.__new__(InventoryManager)
        mgr._cache = None
        assert mgr.count("anything") == 0
        assert mgr.is_full() is False
