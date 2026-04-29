"""Skill 运行时引擎 — 串联解析→状态→控制流→执行"""
import time
import logging
from pathlib import Path
from typing import Optional
from src.skills.models import SkillDSL, SkillResult
from src.skills.dsl_parser import DSLParser
from src.skills.validator import SkillValidator
from src.skills.control_flow import ControlFlowScheduler, SkillContext


class SkillRuntime:
    """Skill 执行引擎"""

    def __init__(self, mod_client, state_manager, action_executor, perception):
        self.mod_client = mod_client
        self.state_manager = state_manager
        self.action_executor = action_executor
        self.perception = perception
        self.parser = DSLParser()
        self.validator = SkillValidator()
        self.control_flow = ControlFlowScheduler()
        self._current_skill: Optional[SkillDSL] = None
        self._interrupted = False
        self.logger = logging.getLogger("blockmind.skill_runtime")

    async def execute_skill(self, skill_path: str) -> SkillResult:
        """执行指定的 DSL Skill 文件"""
        skill = self.parser.parse_file(skill_path)
        return await self.execute_skill_object(skill)

    async def execute_skill_object(self, skill: SkillDSL) -> SkillResult:
        """执行已解析的 SkillDSL 对象"""
        start_time = time.time()
        self._current_skill = skill
        self._interrupted = False

        # 校验
        validation = self.validator.validate_all(skill)
        if not validation.passed:
            return SkillResult(
                success=False, skill_id=skill.skill_id,
                details=f"校验失败: {validation.errors}",
            )

        self.logger.info(f"▶️ 执行 Skill: {skill.name} ({skill.skill_id})")

        # 构建上下文
        ctx = SkillContext(
            state=self.state_manager,
            executor=self.action_executor,
            perception=self.perception,
        )

        # 执行步骤
        try:
            success = await self.control_flow.run_steps(skill.do_steps, ctx)
            duration = int((time.time() - start_time) * 1000)

            result = SkillResult(
                success=success and not self._interrupted,
                skill_id=skill.skill_id,
                details="执行完成" if success else "执行中断",
                duration_ms=duration,
            )

            self.logger.info(f"{'✅' if result.success else '❌'} Skill {skill.name}: {result.details}")
            return result

        except Exception as e:
            self.logger.error(f"Skill 执行异常: {e}")
            return SkillResult(
                success=False, skill_id=skill.skill_id,
                details=f"执行异常: {str(e)}",
            )
        finally:
            self._current_skill = None

    def interrupt(self) -> None:
        """中断当前 Skill 执行"""
        self._interrupted = True
        self.logger.info("⏹️ Skill 执行已中断")

    @property
    def is_running(self) -> bool:
        return self._current_skill is not None
