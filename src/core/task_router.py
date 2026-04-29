"""任务路由器 — 根据分类结果分发到对应处理器"""

import logging
from typing import Optional, Dict, Any

from src.core.task_classifier import TaskClassifier, TaskLevel

logger = logging.getLogger("blockmind.task_router")


class TaskRouter:
    """任务路由器

    根据任务分类结果，将任务分发到对应的处理器：
    - L1_fixed     → 直接执行缓存的 Skill
    - L2_parameter → AI 填充参数 + 执行 Skill
    - L3_template  → AI 填充模板 + 执行
    - L4_dynamic   → AI 完全推理，不缓存
    """

    def __init__(
        self,
        classifier: TaskClassifier,
        skill_runtime=None,
        skill_storage=None,
        ai_decider=None,
        action_executor=None,
    ):
        self.classifier = classifier
        self.skill_runtime = skill_runtime
        self.skill_storage = skill_storage
        self.ai_decider = ai_decider
        self.action_executor = action_executor

    async def route(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """路由任务到对应处理器

        Args:
            task: 自然语言任务描述
            context: 额外上下文（游戏状态等）

        Returns:
            执行结果
        """
        context = context or {}
        level = self.classifier.classify(task)
        logger.info(f"任务路由: [{level}] {task}")

        if level == TaskLevel.L1_FIXED:
            return await self._handle_fixed(task, context)
        elif level == TaskLevel.L2_PARAMETER:
            return await self._handle_parameterized(task, context)
        elif level == TaskLevel.L3_TEMPLATE:
            return await self._handle_template(task, context)
        else:  # L4_dynamic
            return await self._handle_dynamic(task, context)

    async def _handle_fixed(self, task: str, context: dict) -> dict:
        """L1: 直接执行缓存的 Skill"""
        skill_id = self.classifier.get_task_skill_id(task)
        if not skill_id:
            return {"success": False, "error": f"未知固定任务: {task}"}

        if self.skill_storage and self.skill_runtime:
            skill = self.skill_storage.get(skill_id)
            if skill:
                result = await self.skill_runtime.execute_skill_object(skill)
                return {"success": result.success, "details": result.details, "level": "L1"}
            else:
                logger.warning(f"Skill 未找到: {skill_id}，降级为 AI 推理")
                return await self._handle_dynamic(task, context)

        return {"success": False, "error": "Skill 系统未初始化"}

    async def _handle_parameterized(self, task: str, context: dict) -> dict:
        """L2: AI 填充参数 + 执行 Skill"""
        skill_id = self.classifier.get_task_skill_id(task)
        if not skill_id:
            return await self._handle_dynamic(task, context)

        if self.skill_storage and self.skill_runtime and self.ai_decider:
            skill = self.skill_storage.get(skill_id)
            if skill:
                # AI 填充参数
                params = await self.ai_decider.fill_params(task, skill, context)
                result = await self.skill_runtime.execute_skill_object(skill)
                return {"success": result.success, "details": result.details, "level": "L2", "params": params}

        return {"success": False, "error": "Skill 系统未初始化"}

    async def _handle_template(self, task: str, context: dict) -> dict:
        """L3: AI 填充模板 + 执行"""
        if self.ai_decider and self.skill_runtime:
            # AI 生成具体 Skill
            skill = await self.ai_decider.fill_template(task, "", context)
            if skill:
                result = await self.skill_runtime.execute_skill_object(skill)
                return {"success": result.success, "details": result.details, "level": "L3"}

        return {"success": False, "error": "模板填充失败"}

    async def _handle_dynamic(self, task: str, context: dict) -> dict:
        """L4: AI 完全推理，不缓存"""
        if self.ai_decider and self.action_executor:
            actions = await self.ai_decider.reason_dynamic(task, context)
            if actions:
                results = await self.action_executor.execute_sequence(actions)
                return {"success": True, "details": f"执行 {len(actions)} 个动作", "level": "L4", "results": results}

        return {"success": False, "error": "AI 推理失败或动作执行器未初始化"}
