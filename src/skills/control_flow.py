"""控制流调度器 — if/loop/break/wait"""
import ast
import asyncio
import logging
import math
import operator
from typing import List, Any, Optional
from src.skills.models import DoStep, LoopBlock

# 允许的比较运算符
_SAFE_OPS = {
    ast.Gt: operator.gt, ast.Lt: operator.lt,
    ast.GtE: operator.ge, ast.LtE: operator.le,
    ast.Eq: operator.eq, ast.NotEq: operator.ne,
    ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b,
}
# 允许的布尔运算符
_SAFE_BOOL = {ast.And: all, ast.Or: any}
# 允许的一元运算符
_SAFE_UNARY = {ast.Not: operator.not_}
# 允许的方法调用白名单
_SAFE_METHODS = {
    "health", "hunger", "position", "distance_to", "count", "has",
    "is_full", "empty_slots", "used_slots", "any_entity", "block_exists",
    "time", "near", "any_block",
}
# 允许的顶层名称
_SAFE_NAMES = {"self", "inventory", "world", "True", "False", "None"}


class _PlayerAdapter:
    """适配 StateCollector，提供 DSL 期望的 self.* 接口"""
    def __init__(self, state):
        self._state = state

    def health(self) -> float:
        return self._state.player_health

    def hunger(self) -> float:
        return self._state.player_hunger

    def position(self):
        pos = self._state.player_position
        return pos if isinstance(pos, tuple) else (pos.get("x", 0), pos.get("y", 64), pos.get("z", 0))

    def distance_to(self, target) -> float:
        pos = self.position()
        if isinstance(target, (list, tuple)) and len(target) >= 3:
            return math.sqrt(sum((a - b) ** 2 for a, b in zip(pos, target[:3])))
        return 0.0


class _InventoryAdapter:
    """适配 ModClient，提供 DSL 期望的 inventory.* 接口"""
    def __init__(self, mod_client):
        self._client = mod_client
        self._cached_items = []
        self._cached_slots = 36

    async def _refresh(self):
        try:
            inv = await self._client.get_inventory()
            self._cached_items = getattr(inv, "items", [])
            self._cached_slots = getattr(inv, "empty_slots", 36 - len(self._cached_items))
        except Exception:
            pass

    def count(self, item_name: str) -> int:
        return sum(getattr(i, "count", 0) for i in self._cached_items
                   if getattr(i, "name", "") == item_name)

    def has(self, item_name: str) -> bool:
        return self.count(item_name) > 0

    def is_full(self) -> bool:
        return self._cached_slots <= 0

    def empty_slots(self) -> int:
        return max(0, self._cached_slots)

    def used_slots(self) -> int:
        return len(self._cached_items)


class _WorldAdapter:
    """适配 StateCollector + ModClient，提供 DSL 期望的 world.* 接口"""
    def __init__(self, state, mod_client=None):
        self._state = state
        self._client = mod_client

    def time(self) -> int:
        snap = self._state._current_snapshot
        if snap:
            return snap.world.time_of_day
        return 0

    def any_entity(self, entity_type: str = None) -> bool:
        entities = self._state.get_entities_in_radius(32.0, entity_type=entity_type)
        return len(entities) > 0

    def block_exists(self, *args) -> bool:
        return False

    def near(self, radius: float = 16.0):
        return self._state.get_entities_in_radius(radius)

    def any_block(self, block_type: str = None) -> bool:
        if not block_type:
            return False
        blocks = self._state.get_blocks_by_type(block_type, radius=32)
        return len(blocks) > 0


class SkillContext:
    """Skill 执行上下文"""
    def __init__(self, state, executor, perception, variables=None, mod_client=None):
        self.state = state
        self.executor = executor
        self.perception = perception
        self.variables = variables or {}
        self.interrupted = False
        self._mod_client = mod_client
        self._player_adapter = None
        self._inventory_adapter = None
        self._world_adapter = None

    def get_adapters(self):
        """获取 DSL 条件求值用的适配器对象"""
        if self._player_adapter is None:
            self._player_adapter = _PlayerAdapter(self.state)
        if self._inventory_adapter is None:
            self._inventory_adapter = _InventoryAdapter(self._mod_client) if self._mod_client else _InventoryAdapter(None)
        if self._world_adapter is None:
            self._world_adapter = _WorldAdapter(self.state, self._mod_client)
        return self._player_adapter, self._inventory_adapter, self._world_adapter


class ControlFlowScheduler:
    """控制流调度器"""

    def __init__(self):
        self.logger = logging.getLogger("blockmind.control_flow")
        self._max_iterations = 1000

    async def run_steps(self, steps: List[DoStep], ctx: SkillContext) -> bool:
        """执行步骤列表"""
        for step in steps:
            if ctx.interrupted:
                return False
            await self._run_step(step, ctx)
        return True

    async def _run_step(self, step: DoStep, ctx: SkillContext) -> None:
        """执行单个步骤"""
        if step.action == "loop" and step.loop:
            await self.run_loop(step.loop, ctx)
        elif step.action == "if" and step.condition:
            result = await self.evaluate_condition(step.condition, ctx)
            if result and step.if_then:
                await self.run_steps(step.if_then, ctx)
            elif not result and step.if_else:
                await self.run_steps(step.if_else, ctx)
        elif step.action == "wait":
            seconds = step.args.get("value", 1)
            await asyncio.sleep(seconds)
        else:
            await self._execute_action(step, ctx)

    async def run_loop(self, loop: LoopBlock, ctx: SkillContext) -> bool:
        """执行循环"""
        iterations = 0
        if loop.while_condition:
            while iterations < loop.max_iterations:
                if ctx.interrupted:
                    return False
                if not await self.evaluate_condition(loop.while_condition, ctx):
                    break
                await self.run_steps(loop.do_steps, ctx)
                iterations += 1
        elif loop.over_variable:
            items = ctx.variables.get(loop.over_variable, [])
            for item in items:
                if ctx.interrupted:
                    return False
                ctx.variables["item"] = item
                await self.run_steps(loop.do_steps, ctx)
                iterations += 1
        return True

    async def evaluate_condition(self, expr: str, ctx: SkillContext) -> bool:
        """安全评估条件表达式（AST 白名单，无 eval）"""
        try:
            tree = ast.parse(expr, mode="eval")
            result = self._safe_eval(tree.body, ctx)
            return bool(result)
        except Exception as e:
            self.logger.warning(f"条件评估失败: {expr} -> {e}")
            return False

    def _safe_eval(self, node: ast.AST, ctx: SkillContext) -> Any:
        """递归安全求值 AST 节点"""
        # 数值/字符串/布尔常量
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float, str, bool, type(None))):
                return node.value
            raise ValueError(f"不允许的常量类型: {type(node.value)}")

        # 名称引用（白名单）
        if isinstance(node, ast.Name):
            if node.id in _SAFE_NAMES:
                player, inventory, world = ctx.get_adapters()
                return {"self": player, "inventory": inventory,
                        "world": world, "True": True, "False": False,
                        "None": None}.get(node.id)
            if node.id in ctx.variables:
                return ctx.variables[node.id]
            raise ValueError(f"不允许的名称: {node.id}")

        # 属性访问
        if isinstance(node, ast.Attribute):
            obj = self._safe_eval(node.value, ctx)
            if node.attr not in _SAFE_METHODS and node.attr not in {
                "health", "hunger", "position", "count", "has",
                "is_full", "empty_slots", "used_slots", "time",
            }:
                raise ValueError(f"不允许的属性: {node.attr}")
            return getattr(obj, node.attr)

        # 方法调用
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Attribute):
                raise ValueError("只允许方法调用，不允许顶层函数调用")
            method_name = node.func.attr
            if method_name not in _SAFE_METHODS:
                raise ValueError(f"不允许的方法: {method_name}")
            obj = self._safe_eval(node.func.value, ctx)
            args = [self._safe_eval(a, node) for a in node.args]
            kwargs = {kw.arg: self._safe_eval(kw.value, ctx) for kw in node.keywords}
            return getattr(obj, method_name)(*args, **kwargs)

        # 比较运算
        if isinstance(node, ast.Compare):
            left = self._safe_eval(node.left, ctx)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._safe_eval(comparator, ctx)
                op_type = type(op)
                if op_type not in _SAFE_OPS:
                    raise ValueError(f"不允许的运算符: {op_type.__name__}")
                if not _SAFE_OPS[op_type](left, right):
                    return False
                left = right
            return True

        # 布尔运算 (and/or)
        if isinstance(node, ast.BoolOp):
            op_func = _SAFE_BOOL.get(type(node.op))
            if not op_func:
                raise ValueError(f"不允许的布尔运算: {type(node.op).__name__}")
            values = [self._safe_eval(v, ctx) for v in node.values]
            return op_func(values)

        # 一元运算 (not)
        if isinstance(node, ast.UnaryOp):
            op_func = _SAFE_UNARY.get(type(node.op))
            if not op_func:
                raise ValueError(f"不允许的一元运算: {type(node.op).__name__}")
            return op_func(self._safe_eval(node.operand, ctx))

        raise ValueError(f"不允许的 AST 节点: {type(node).__name__}")

    async def _execute_action(self, step: DoStep, ctx: SkillContext) -> Any:
        """执行具体动作"""
        action_map = {
            "walk_to": lambda args: ctx.executor.walk_to(**self._parse_pos(args)),
            "dig_block": lambda args: ctx.executor.dig_block(**self._parse_pos(args)),
            "place_block": lambda args: ctx.executor.place_block(args.get("item", ""), **self._parse_pos(args)),
            "attack": lambda args: ctx.executor.attack(args.get("entity_id", 0)),
            "eat": lambda args: ctx.executor.eat(args.get("item", "")),
            "look_at": lambda args: ctx.executor.look_at(**self._parse_pos(args)),
            "chat": lambda args: ctx.executor.send_chat(args.get("message", "")),
            "wait": lambda args: asyncio.sleep(args.get("seconds", 1)),
            "use_item": lambda args: ctx.executor.use_item(args.get("item", ""), args.get("hand", "main")),
            "equip_item": lambda args: ctx.executor.equip_item(args.get("item", ""), args.get("slot", "mainhand")),
            "drop_item": lambda args: ctx.executor.drop_item(args.get("item", ""), args.get("count", 1)),
        }
        handler = action_map.get(step.action)
        if handler:
            return await handler(step.args)
        else:
            self.logger.warning(f"未知动作: {step.action}")

    def _parse_pos(self, args: dict) -> dict:
        """解析位置参数"""
        if isinstance(args, dict) and "x" in args:
            return args
        return {"x": 0, "y": 64, "z": 0}
