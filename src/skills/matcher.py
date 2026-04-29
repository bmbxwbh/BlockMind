"""Skill 意图匹配器 — 根据任务描述匹配最合适的 Skill"""
import logging
from typing import List, Optional
from src.skills.models import SkillDSL
from src.skills.storage import SkillStorage


class SkillMatcher:
    """Skill 意图匹配器"""

    def __init__(self, storage: SkillStorage):
        self.storage = storage
        self.logger = logging.getLogger("blockmind.skill_matcher")

    def match(self, task: str, game_state: dict = None) -> Optional[SkillDSL]:
        """匹配最合适的 Skill"""
        # 1. 精确匹配 skill_id
        skill = self.storage.get(task)
        if skill:
            return skill

        # 2. 名称匹配
        candidates = self.storage.search(task)
        if candidates:
            return self.match_by_priority(candidates)

        # 3. 标签匹配
        tags = task.lower().split()
        tag_matches = self.match_by_tags(tags)
        if tag_matches:
            return self.match_by_priority(tag_matches)

        return None

    def match_by_tags(self, tags: List[str]) -> List[SkillDSL]:
        """按标签匹配"""
        results = []
        for skill in self.storage.list_all():
            skill_tags = [t.lower() for t in skill.tags]
            if any(tag in skill_tags for tag in tags):
                results.append(skill)
        return results

    def match_by_priority(self, skills: List[SkillDSL]) -> SkillDSL:
        """按优先级选择（数字越小优先级越高）"""
        return min(skills, key=lambda s: s.priority)
