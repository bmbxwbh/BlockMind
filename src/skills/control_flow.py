"""控制流调度器 — if/loop/break/wait"""
import asyncio
import logging
from typing import List, Any
from src.skills.models import DoStep, LoopBlock


class SkillContext:
    """Skill 执行上下文"""
    def __init__(self, state, executor, perception, variables=None):
        self.state = state
        self.executor = executor
        self.perception = perception
        self.variables = variables or {}
        self.interrupted = False


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
        """评估条件表达式"""
        try:
            safe_vars = {
                "self": ctx.state,
                "inventory": ctx.state,
                "world": ctx.state,
                **ctx.variables,
            }
            return bool(eval(expr, {"__builtins__": {}}, safe_vars))
        except Exception as e:
            self.logger.warning(f"条件评估失败: {expr} -> {e}")
            return False

    async def _execute_action(self, step: DoStep, ctx: SkillContext) -> Any:
        """执行具体动作"""
        action_map = {
            "walk_to": lambda args: ctx.executor.walk_to(**self._parse_pos(args)),
            "dig_block": lambda args: ctx.executor.dig_block(**self._parse_pos(args)),
            "place_block": lambda args: ctx.executor.place_block(args.get("item", ""), **self._parse_pos(args)),
            "attack": lambda args: ctx.executor.attack(args.get("entity_id", 0)),
            "eat": lambda args: ctx.executor.eat(args.get("item", "")),
            "look_at": lambda args: ctx.executor.look_at(**self._parse_pos(args)),
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
