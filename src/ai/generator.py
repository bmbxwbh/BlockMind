"""DSL 生成器 — 自然语言 → Skill DSL"""
import yaml
import logging
from typing import List, Dict
from src.ai.provider import AIProvider
from src.ai.prompts import PROMPTS
from src.skills.models import SkillDSL
from src.skills.dsl_parser import DSLParser
from src.skills.validator import SkillValidator


class DSLGenerator:
    """AI DSL 生成器"""

    def __init__(self, provider: AIProvider):
        self.provider = provider
        self.parser = DSLParser()
        self.validator = SkillValidator()
        self.logger = logging.getLogger("blockmind.dsl_generator")

    async def generate_skill(self, task: str, game_state: dict) -> SkillDSL:
        """将自然语言任务转换为 Skill DSL"""
        prompt = PROMPTS["skill_generation"].format(
            task_description=task,
            game_state=str(game_state),
            available_functions="walk_to, dig_block, place_block, attack, eat, scan_entities, wait",
        )
        messages = [{"role": "user", "content": prompt}]

        for attempt in range(3):
            try:
                yaml_text = await self.provider.chat(messages)
                yaml_text = yaml_text.strip().strip("```yaml").strip("```")
                skill = self.parser.parse_yaml(yaml_text)
                validation = self.validator.validate_all(skill)
                if validation.passed:
                    return skill
                self.logger.warning(f"校验失败 (第{attempt+1}次): {validation.errors}")
            except Exception as e:
                self.logger.warning(f"生成失败 (第{attempt+1}次): {e}")

        raise RuntimeError(f"无法生成有效的 Skill: {task}")

    async def fill_params(self, task: str, skill: SkillDSL, context: dict) -> dict:
        """L2 参数填充"""
        prompt = PROMPTS["parameter_fill"].format(
            task=task, skill_name=skill.name, game_state=str(context),
        )
        result = await self.provider.chat([{"role": "user", "content": prompt}])
        import json
        return json.loads(result.strip().strip("```json").strip("```"))

    async def fill_template(self, task: str, template: str, context: dict) -> SkillDSL:
        """L3 模板填充"""
        prompt = PROMPTS["template_fill"].format(
            task=task, template=template, game_state=str(context),
        )
        yaml_text = await self.provider.chat([{"role": "user", "content": prompt}])
        yaml_text = yaml_text.strip().strip("```yaml").strip("```")
        return self.parser.parse_yaml(yaml_text)

    async def reason_dynamic(self, task: str, context: dict) -> List[Dict]:
        """L4 动态推理 — 直接输出动作序列"""
        prompt = f"任务：{task}\n状态：{context}\n输出动作序列 JSON 数组。"
        result = await self.provider.chat([{"role": "user", "content": prompt}])
        import json
        return json.loads(result.strip().strip("```json").strip("```"))
