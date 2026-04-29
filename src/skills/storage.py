"""Skill 存储管理 — 文件 CRUD + 索引 + 版本控制"""
import yaml
import shutil
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from src.skills.models import SkillDSL
from src.skills.dsl_parser import DSLParser


class SkillStorage:
    """Skill 文件存储管理"""

    def __init__(self, storage_path: str = "./skills", max_versions: int = 10):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.max_versions = max_versions
        self.parser = DSLParser()
        self.logger = logging.getLogger("blockmind.skill_storage")
        self._cache: dict = {}  # skill_id -> SkillDSL

    def save(self, skill: SkillDSL, category: str = "custom") -> None:
        """保存 Skill 到文件"""
        dir_path = self.storage_path / category
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = dir_path / f"{skill.skill_id}.yaml"

        # 版本控制：备份旧版本
        if file_path.exists():
            self._create_backup(file_path)

        data = skill.model_dump(exclude_none=True)
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

        self._cache[skill.skill_id] = skill
        self.logger.info(f"💾 保存 Skill: {skill.skill_id}")

    def get(self, skill_id: str) -> Optional[SkillDSL]:
        """获取 Skill（优先缓存）"""
        if skill_id in self._cache:
            return self._cache[skill_id]

        # 搜索文件
        for yaml_file in self.storage_path.rglob("*.yaml"):
            try:
                skill = self.parser.parse_file(str(yaml_file))
                if skill.skill_id == skill_id:
                    self._cache[skill_id] = skill
                    return skill
            except Exception:
                continue
        return None

    def list_all(self, category: str = None) -> List[SkillDSL]:
        """列出所有 Skill"""
        skills = []
        search_path = self.storage_path / category if category else self.storage_path
        for yaml_file in search_path.rglob("*.yaml"):
            try:
                skills.append(self.parser.parse_file(str(yaml_file)))
            except Exception as e:
                self.logger.warning(f"解析失败: {yaml_file} -> {e}")
        return skills

    def delete(self, skill_id: str) -> bool:
        """删除 Skill"""
        for yaml_file in self.storage_path.rglob("*.yaml"):
            try:
                skill = self.parser.parse_file(str(yaml_file))
                if skill.skill_id == skill_id:
                    yaml_file.unlink()
                    self._cache.pop(skill_id, None)
                    self.logger.info(f"🗑️ 删除 Skill: {skill_id}")
                    return True
            except Exception:
                continue
        return False

    def search(self, query: str) -> List[SkillDSL]:
        """搜索 Skill（按名称/标签）"""
        results = []
        for skill in self.list_all():
            if (query.lower() in skill.name.lower() or
                any(query.lower() in tag.lower() for tag in skill.tags)):
                results.append(skill)
        return results

    def update_stats(self, skill_id: str, success: bool) -> None:
        """更新 Skill 使用统计"""
        skill = self.get(skill_id)
        if skill:
            skill.usage_count += 1
            # 滑动平均成功率
            skill.success_rate = (
                (skill.success_rate * (skill.usage_count - 1) + (1 if success else 0))
                / skill.usage_count
            )
            self.save(skill)

    def _create_backup(self, file_path: Path) -> None:
        """创建版本备份"""
        backup_dir = file_path.parent / ".versions"
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{file_path.stem}_{timestamp}.yaml"
        shutil.copy2(file_path, backup_path)

        # 清理旧版本
        backups = sorted(backup_dir.glob(f"{file_path.stem}_*.yaml"))
        while len(backups) > self.max_versions:
            backups.pop(0).unlink()
