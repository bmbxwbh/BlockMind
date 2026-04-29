"""DSL 解析器 — YAML → SkillDSL"""
import yaml
import logging
from pathlib import Path
from typing import List, Optional
from src.skills.models import SkillDSL, WhenClause, DoStep, LoopBlock, UntilClause


class DSLParser:
    """将 YAML Skill 文件解析为 SkillDSL 对象"""

    def __init__(self):
        self.logger = logging.getLogger("blockmind.dsl_parser")

    def parse_file(self, file_path: str) -> SkillDSL:
        """从文件路径解析"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Skill 文件不存在: {file_path}")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return self.parse_dict(data)

    def parse_yaml(self, yaml_content: str) -> SkillDSL:
        """从 YAML 字符串解析"""
        data = yaml.safe_load(yaml_content)
        return self.parse_dict(data)

    def parse_dict(self, data: dict) -> SkillDSL:
        """从字典解析"""
        when = WhenClause(**data.get("when", {}))
        until = UntilClause(**data.get("until", {}))
        do_steps = self._parse_do(data.get("do", []))

        return SkillDSL(
            skill_id=data["skill_id"],
            name=data["name"],
            tags=data.get("tags", []),
            priority=data.get("priority", 5),
            when=when,
            do_steps=do_steps,
            until=until,
            description=data.get("description", ""),
            author=data.get("author", "system"),
            version=data.get("version", 1),
            task_level=data.get("task_level", "L2"),
        )

    def _parse_do(self, do_data: list) -> List[DoStep]:
        """解析 do 子句"""
        steps = []
        for item in do_data:
            if isinstance(item, dict):
                if "loop" in item:
                    loop_data = item["loop"]
                    loop = LoopBlock(
                        while_condition=loop_data.get("while"),
                        over_variable=loop_data.get("over"),
                        do_steps=self._parse_do(loop_data.get("do", [])),
                    )
                    steps.append(DoStep(action="loop", loop=loop))
                elif "if" in item:
                    steps.append(DoStep(
                        action="if",
                        condition=item["if"],
                        if_then=self._parse_do(item.get("then", [])),
                        if_else=self._parse_do(item.get("else", [])),
                    ))
                else:
                    for action, args in item.items():
                        steps.append(DoStep(action=action, args=args if isinstance(args, dict) else {"value": args}))
            elif isinstance(item, str):
                steps.append(DoStep(action=item))
        return steps

    def validate_syntax(self, skill: SkillDSL) -> List[str]:
        """基础语法校验"""
        errors = []
        if not skill.skill_id:
            errors.append("skill_id 不能为空")
        if not skill.name:
            errors.append("name 不能为空")
        if skill.priority < 1 or skill.priority > 5:
            errors.append("priority 必须在 1-5 之间")
        if not skill.do_steps:
            errors.append("do 不能为空")
        return errors
