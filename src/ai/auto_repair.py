"""Skill 自动修复"""
import logging
from src.ai.provider import AIProvider
from src.ai.prompts import PROMPTS
from src.skills.models import SkillDSL
from src.skills.dsl_parser import DSLParser
from src.skills.validator import SkillValidator


class SkillAutoRepairer:
    """Skill 自动修复器"""

    def __init__(self, provider: AIProvider):
        self.provider = provider
        self.parser = DSLParser()
        self.validator = SkillValidator()
        self.logger = logging.getLogger("blockmind.auto_repair")

    async def analyze_error(self, skill: SkillDSL, error: Exception) -> str:
        """分析错误原因"""
        prompt = PROMPTS["error_analysis"].format(
            skill_dsl=skill.model_dump_json(),
            error_message=str(error),
            execution_log="",
        )
        return await self.provider.chat([{"role": "user", "content": prompt}])

    async def repair_skill(self, skill: SkillDSL, analysis: str) -> SkillDSL:
        """修复 Skill"""
        prompt = PROMPTS["skill_repair"].format(
            original_skill=skill.model_dump_json(),
            error_analysis=analysis,
        )
        yaml_text = await self.provider.chat([{"role": "user", "content": prompt}])
        yaml_text = yaml_text.strip().strip("```yaml").strip("```")
        repaired = self.parser.parse_yaml(yaml_text)
        repaired.skill_id = skill.skill_id  # 保持原 ID
        repaired.version = skill.version + 1
        return repaired

    async def validate_repair(self, original: SkillDSL, repaired: SkillDSL) -> bool:
        """验证修复结果"""
        validation = self.validator.validate_all(repaired)
        return validation.passed
