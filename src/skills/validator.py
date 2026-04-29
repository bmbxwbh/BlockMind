"""Skill DSL 校验器"""
import re
import logging
from typing import List
from src.skills.models import SkillDSL, ValidationResult


class SkillValidator:
    """Skill DSL 校验器 — 语法 + 安全 + 逻辑"""

    FORBIDDEN_PATTERNS = [
        "rm -rf", "suicide", "place_command_block",
        "kill @a", "kill @p", "summon wither",
    ]

    HARDCODE_PATTERNS = [
        r"position\s*:\s*\(\d+,\s*\d+,\s*\d+\)",
    ]

    def __init__(self):
        self.logger = logging.getLogger("blockmind.validator")

    def validate_syntax(self, skill: SkillDSL) -> ValidationResult:
        """语法校验"""
        errors = []
        if not skill.skill_id:
            errors.append("skill_id 不能为空")
        if not skill.name:
            errors.append("name 不能为空")
        if skill.priority < 1 or skill.priority > 5:
            errors.append("priority 必须在 1-5 之间")
        if not skill.do_steps:
            errors.append("do 步骤不能为空")
        return ValidationResult(passed=len(errors) == 0, errors=errors)

    def validate_safety(self, skill: SkillDSL) -> ValidationResult:
        """安全性校验"""
        errors = []
        content = skill.model_dump_json()
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern in content.lower():
                errors.append(f"包含禁止操作: {pattern}")
        return ValidationResult(passed=len(errors) == 0, errors=errors)

    def validate_logic(self, skill: SkillDSL, game_state: dict = None) -> ValidationResult:
        """逻辑合理性校验"""
        warnings = []
        if len(skill.do_steps) > 50:
            warnings.append("步骤过多（>50），可能导致执行时间过长")
        return ValidationResult(passed=True, warnings=warnings)

    def validate_all(self, skill: SkillDSL, game_state: dict = None) -> ValidationResult:
        """执行全部校验"""
        results = [
            self.validate_syntax(skill),
            self.validate_safety(skill),
            self.validate_logic(skill, game_state),
        ]
        all_errors = []
        all_warnings = []
        for r in results:
            all_errors.extend(r.errors)
            all_warnings.extend(r.warnings)
        return ValidationResult(
            passed=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
        )
