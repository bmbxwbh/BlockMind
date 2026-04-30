"""DSL 生成器 — 自然语言 → Skill DSL"""
import json
import yaml
import logging
from typing import List, Dict
from src.ai.provider import AIProvider
from src.ai.prompts import PROMPTS, DSL_SYNTAX_REFERENCE
from src.skills.models import SkillDSL
from src.skills.dsl_parser import DSLParser
from src.skills.validator import SkillValidator


class DSLGenerator:
    """AI DSL 生成器

    将自然语言任务转换为 Skill DSL，支持四级任务分类：
    - L1: 直接返回缓存 Skill
    - L2: AI 填充参数
    - L3: AI 填充模板
    - L4: AI 完全推理
    """

    def __init__(self, provider: AIProvider):
        self.provider = provider
        self.parser = DSLParser()
        self.validator = SkillValidator()
        self.logger = logging.getLogger("blockmind.dsl_generator")

    async def generate_skill(self, task: str, game_state: dict) -> SkillDSL:
        """将自然语言任务转换为 Skill DSL（L1/L2 生成）"""
        prompt = PROMPTS["skill_generation"].format(
            task_description=task,
            game_state=str(game_state),
            available_functions="walk_to, dig_block, place_block, attack, eat, look_at, scan_blocks, scan_entities, wait",
            dsl_ref=DSL_SYNTAX_REFERENCE,
        )
        messages = [{"role": "user", "content": prompt}]

        for attempt in range(3):
            try:
                yaml_text = await self.provider.chat(messages, temperature=0.3)
                yaml_text = yaml_text.strip()
                # 清理可能的代码块标记
                if yaml_text.startswith("```"):
                    yaml_text = yaml_text.split("\n", 1)[1]
                if yaml_text.endswith("```"):
                    yaml_text = yaml_text.rsplit("```", 1)[0]
                yaml_text = yaml_text.strip()

                skill = self.parser.parse_yaml(yaml_text)
                validation = self.validator.validate_all(skill)
                if validation.passed:
                    self.logger.info(f"Skill 生成成功: {skill.skill_id} (第{attempt+1}次)")
                    return skill
                self.logger.warning(f"校验失败 (第{attempt+1}次): {validation.errors}")
            except Exception as e:
                self.logger.warning(f"生成失败 (第{attempt+1}次): {e}")

        raise RuntimeError(f"无法生成有效的 Skill: {task}")

    async def fill_params(self, task: str, skill: SkillDSL, context: dict) -> dict:
        """L2 参数填充 — 为已有 Skill 填入具体目标参数"""
        prompt = PROMPTS["parameter_fill"].format(
            task=task,
            skill_name=skill.name,
            game_state=str(context),
        )
        result = await self.provider.chat([{"role": "user", "content": prompt}], temperature=0.2)
        result = result.strip()
        # 清理代码块标记
        if result.startswith("```"):
            result = result.split("\n", 1)[1]
        if result.endswith("```"):
            result = result.rsplit("```", 1)[0]
        return json.loads(result.strip())

    async def fill_template(self, task: str, template: str, context: dict) -> SkillDSL:
        """L3 模板填充 — 基于模板结构生成完整 Skill"""
        prompt = PROMPTS["template_fill"].format(
            task=task,
            template=template,
            game_state=str(context),
            dsl_ref=DSL_SYNTAX_REFERENCE,
        )
        yaml_text = await self.provider.chat([{"role": "user", "content": prompt}], temperature=0.3)
        yaml_text = yaml_text.strip()
        if yaml_text.startswith("```"):
            yaml_text = yaml_text.split("\n", 1)[1]
        if yaml_text.endswith("```"):
            yaml_text = yaml_text.rsplit("```", 1)[0]
        return self.parser.parse_yaml(yaml_text.strip())

    async def reason_dynamic(self, task: str, context: dict) -> List[Dict]:
        """L4 动态推理 — AI 完全推理，输出动作序列"""
        prompt = f"""你是 Minecraft AI 助手，直接为任务规划动作序列。

## 任务：{task}

## 当前游戏状态
{context}

## 输出要求
只输出 JSON 数组，每个元素是一个动作对象。可用动作：
- walk_to: {{"action": "walk_to", "x": 数字, "y": 数字, "z": 数字}}
- dig_block: {{"action": "dig_block", "x": 数字, "y": 数字, "z": 数字}}
- place_block: {{"action": "place_block", "item": "物品名", "x": 数字, "y": 数字, "z": 数字}}
- attack: {{"action": "attack", "entity_id": 数字}}
- eat: {{"action": "eat", "item": "物品名"}}
- wait: {{"action": "wait", "seconds": 数字}}

不要包含任何解释文字。
"""
        result = await self.provider.chat([{"role": "user", "content": prompt}], temperature=0.3)
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[1]
        if result.endswith("```"):
            result = result.rsplit("```", 1)[0]
        return json.loads(result.strip())
