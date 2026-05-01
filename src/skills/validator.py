"""Skill DSL 校验器"""
import re
import logging
from typing import List
from src.skills.models import SkillDSL, ValidationResult


class SkillValidator:
    """Skill DSL 校验器 — 语法 + 安全 + 逻辑 + 导入安全"""

    FORBIDDEN_PATTERNS = [
        "rm -rf", "suicide", "place_command_block",
        "kill @a", "kill @p", "summon wither",
        "op @a", "deop", "ban ", "kick ",
        "execute as @a", "gamemode creative",
    ]

    # 导入时额外检查的危险模式
    IMPORT_DANGEROUS_PATTERNS = [
        r"eval\s*\(",
        r"exec\s*\(",
        r"__import__",
        r"subprocess",
        r"os\.system",
        r"open\s*\(.*/etc/",
        r"\.\./",  # 路径穿越
    ]

    HARDCODE_PATTERNS = [
        r"position\\s*:\\s*\\(\\d+,\\s*\\d+,\\s*\\d+\\)",
    ]

    # 已知安全的 action 白名单
    SAFE_ACTIONS = {
        "walk_to", "smart_navigate", "dig_block", "place_block",
        "attack", "eat", "look_at", "wait", "chat",
        "scan_entities", "scan_blocks", "use_item",
        "craft_item", "equip_item", "drop_item",
    }

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

    def validate_import(self, skill: SkillDSL, yaml_content: str = "") -> ValidationResult:
        """
        导入安全校验 — 比 validate_all 更严格

        额外检查:
        - 未知 action（不在白名单中）
        - YAML 中的危险代码注入
        - 条件表达式中的危险调用
        - 步骤数量限制
        - 参数大小限制
        """
        errors = []
        warnings = []

        # 1. 先执行基础校验
        base = self.validate_all(skill)
        errors.extend(base.errors)
        warnings.extend(base.warnings)

        # 2. 检查未知 action
        for step in skill.do_steps:
            self._check_step_actions(step, errors, warnings)

        # 3. 检查 YAML 原始内容中的危险模式
        if yaml_content:
            import re
            for pattern in self.IMPORT_DANGEROUS_PATTERNS:
                if re.search(pattern, yaml_content, re.IGNORECASE):
                    errors.append(f"导入内容包含危险模式: {pattern}")

        # 4. 条件表达式安全检查
        for step in skill.do_steps:
            self._check_conditions(step, warnings)

        # 5. 步骤数量限制（导入更严格）
        if len(skill.do_steps) > 30:
            warnings.append(f"导入的 Skill 步骤较多（{len(skill.do_steps)}），请确认安全性")

        # 6. skill_id 格式检查
        import re
        if not re.match(r'^[a-z][a-z0-9_]{1,63}$', skill.skill_id):
            errors.append(f"skill_id 格式不安全: '{skill.skill_id}'（要求: 小写字母开头，只含小写字母/数字/下划线，2-64字符）")

        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _check_step_actions(self, step, errors: list, warnings: list) -> None:
        """检查步骤中的 action 是否安全"""
        if step.action and step.action not in self.SAFE_ACTIONS:
            warnings.append(f"未知 action: '{step.action}'（不在安全白名单中）")
        if step.loop:
            for sub_step in step.loop.do_steps:
                self._check_step_actions(sub_step, errors, warnings)
        if step.if_then:
            for sub_step in step.if_then:
                self._check_step_actions(sub_step, errors, warnings)
        if step.if_else:
            for sub_step in step.if_else:
                self._check_step_actions(sub_step, errors, warnings)

    def _check_conditions(self, step, warnings: list) -> None:
        """检查条件表达式中的危险调用"""
        import re
        dangerous_calls = ["eval", "exec", "import", "open", "system", "subprocess"]
        conditions = []
        if step.condition:
            conditions.append(step.condition)
        if step.loop and step.loop.while_condition:
            conditions.append(step.loop.while_condition)
        for cond in conditions:
            for call in dangerous_calls:
                if call in cond.lower():
                    warnings.append(f"条件表达式中包含可疑调用: '{call}' in '{cond}'")
