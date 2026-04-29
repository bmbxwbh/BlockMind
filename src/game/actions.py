"""动作执行器 — 通过 Mod API 执行游戏动作，支持安全校验"""

import logging
from typing import Optional

from src.mod_client.client import ModClient
from src.mod_client.models import ActionResult

logger = logging.getLogger("blockmind.actions")


class ActionExecutor:
    """动作执行器

    封装 Mod API 的动作执行，提供高级游戏动作接口。
    支持可选的安全网关（SafetyGateway）对高风险动作进行拦截。
    """

    def __init__(self, mod_client: ModClient, safety_gateway=None):
        self.mod_client = mod_client
        self.safety_gateway = safety_gateway

    async def _safe_check(self, action: str, context: dict = None) -> bool:
        """安全校验（如果有安全网关）"""
        if self.safety_gateway is None:
            return True
        return await self.safety_gateway.check(action, context or {})

    async def walk_to(self, x: float, y: float, z: float, sprint: bool = False) -> ActionResult:
        """移动到指定位置"""
        if not await self._safe_check("move", {"x": x, "y": y, "z": z}):
            return ActionResult(success=False, details="安全校验拒绝")
        result = await self.mod_client.move(x, y, z, sprint)
        logger.info(f"移动到 ({x}, {y}, {z}): {result.success}")
        return result

    async def dig_block(self, x: int, y: int, z: int) -> ActionResult:
        """挖掘方块"""
        if not await self._safe_check("dig", {"x": x, "y": y, "z": z}):
            return ActionResult(success=False, details="安全校验拒绝")
        result = await self.mod_client.dig(x, y, z)
        logger.info(f"挖掘 ({x}, {y}, {z}): {result.success}")
        return result

    async def place_block(self, item: str, x: int, y: int, z: int) -> ActionResult:
        """放置方块"""
        if not await self._safe_check("place", {"item": item, "x": x, "y": y, "z": z}):
            return ActionResult(success=False, details="安全校验拒绝")
        result = await self.mod_client.place(item, x, y, z)
        logger.info(f"放置 {item} 到 ({x}, {y}, {z}): {result.success}")
        return result

    async def attack(self, entity_id: int) -> ActionResult:
        """攻击实体"""
        if not await self._safe_check("attack", {"entity_id": entity_id}):
            return ActionResult(success=False, details="安全校验拒绝")
        result = await self.mod_client.attack(entity_id)
        logger.info(f"攻击实体 {entity_id}: {result.success}")
        return result

    async def eat(self, item: str) -> ActionResult:
        """进食"""
        if not await self._safe_check("eat", {"item": item}):
            return ActionResult(success=False, details="安全校验拒绝")
        result = await self.mod_client.eat(item)
        logger.info(f"进食 {item}: {result.success}")
        return result

    async def look_at(self, x: float, y: float, z: float) -> ActionResult:
        """看向指定位置"""
        if not await self._safe_check("look", {"x": x, "y": y, "z": z}):
            return ActionResult(success=False, details="安全校验拒绝")
        result = await self.mod_client.look(x, y, z)
        return result

    async def send_chat(self, message: str) -> ActionResult:
        """发送聊天消息"""
        if not await self._safe_check("chat", {"message": message}):
            return ActionResult(success=False, details="安全校验拒绝")
        result = await self.mod_client.chat(message)
        logger.info(f"聊天: {message}")
        return result

    async def jump(self) -> ActionResult:
        """跳跃（通过短暂移动模拟）"""
        status = await self.mod_client.get_status()
        pos = status.position
        return await self.walk_to(pos["x"], pos["y"] + 1, pos["z"])

    async def execute_sequence(self, actions: list) -> list:
        """执行动作序列

        Args:
            actions: 动作列表，每个元素为 dict，包含 action 和参数
                     例: [{"action": "walk_to", "x": 1, "y": 2, "z": 3}, ...]

        Returns:
            执行结果列表
        """
        results = []
        for act in actions:
            action_type = act.get("action", "")
            if action_type == "walk_to":
                r = await self.walk_to(act["x"], act["y"], act["z"], act.get("sprint", False))
            elif action_type == "dig":
                r = await self.dig_block(act["x"], act["y"], act["z"])
            elif action_type == "place":
                r = await self.place_block(act["item"], act["x"], act["y"], act["z"])
            elif action_type == "attack":
                r = await self.attack(act["entity_id"])
            elif action_type == "eat":
                r = await self.eat(act["item"])
            elif action_type == "look":
                r = await self.look_at(act["x"], act["y"], act["z"])
            elif action_type == "chat":
                r = await self.send_chat(act["message"])
            elif action_type == "wait":
                import asyncio
                await asyncio.sleep(act.get("seconds", 1))
                r = ActionResult(success=True, details=f"等待 {act.get('seconds', 1)}s")
            else:
                logger.warning(f"未知动作类型: {action_type}")
                r = ActionResult(success=False, details=f"未知动作: {action_type}")
            results.append({"action": action_type, "result": r})
            if not r.success:
                logger.warning(f"动作序列中断于: {action_type} — {r.details}")
                break
        return results
