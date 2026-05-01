"""Skill 市场管理器 — 导入/导出/安装/卸载"""
import yaml
import json
import shutil
import logging
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from src.skills.models import SkillDSL, SkillMarketMeta
from src.skills.dsl_parser import DSLParser
from src.skills.validator import SkillValidator


class SkillMarketplace:
    """Skill 市场管理器"""

    CATEGORIES = [
        "combat", "farming", "building", "gathering",
        "navigation", "storage", "survival", "automation", "general"
    ]

    def __init__(self, storage_path: str = "./skills", skill_storage=None):
        self.storage_path = Path(storage_path)
        self.marketplace_path = self.storage_path / "marketplace"
        self.custom_path = self.storage_path / "custom"
        self.marketplace_path.mkdir(parents=True, exist_ok=True)
        self.custom_path.mkdir(parents=True, exist_ok=True)
        self.parser = DSLParser()
        self.validator = SkillValidator()
        self.skill_storage = skill_storage
        self.logger = logging.getLogger("blockmind.marketplace")
        self._index: Dict[str, dict] = {}  # skill_id -> metadata
        self._load_index()

    # ── 索引管理 ──

    def _index_path(self) -> Path:
        return self.marketplace_path / ".index.json"

    def _load_index(self) -> None:
        """加载本地市场索引"""
        path = self._index_path()
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self._index = json.load(f)
            except Exception as e:
                self.logger.warning(f"索引加载失败: {e}")
                self._index = {}

    def _save_index(self) -> None:
        """保存本地市场索引"""
        with open(self._index_path(), "w", encoding="utf-8") as f:
            json.dump(self._index, f, ensure_ascii=False, indent=2)

    # ── 导出 ──

    def export_skill(self, skill_id: str, include_meta: bool = True) -> Optional[str]:
        """
        导出 Skill 为可分享的 YAML 字符串

        Returns:
            YAML 字符串，失败返回 None
        """
        skill = self._get_skill(skill_id)
        if not skill:
            self.logger.error(f"导出失败: Skill {skill_id} 不存在")
            return None

        data = self._skill_to_export_dict(skill, include_meta)
        return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)

    def export_to_file(self, skill_id: str, output_path: str) -> bool:
        """导出 Skill 到文件"""
        content = self.export_skill(skill_id)
        if not content:
            return False
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self.logger.info(f"📤 导出 Skill: {skill_id} -> {output_path}")
        return True

    def export_bundle(self, skill_ids: List[str], output_dir: str) -> bool:
        """批量导出多个 Skill 到目录"""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        exported = 0
        for sid in skill_ids:
            if self.export_to_file(sid, str(out / f"{sid}.yaml")):
                exported += 1
        # 生成 manifest
        manifest = {
            "name": "BlockMind Skill Bundle",
            "version": "1.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "skills": skill_ids,
            "count": exported,
        }
        with open(out / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        self.logger.info(f"📦 导出 Bundle: {exported} 个 Skill -> {output_dir}")
        return exported > 0

    # ── 导入 ──

    def import_from_yaml(self, yaml_content: str, force: bool = False) -> Optional[SkillDSL]:
        """
        从 YAML 内容导入 Skill

        Args:
            yaml_content: YAML 字符串
            force: 强制覆盖已存在的同 ID Skill

        Returns:
            导入的 SkillDSL，失败返回 None
        """
        # 1. 解析 YAML
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            self.logger.error(f"YAML 解析失败: {e}")
            return None

        if not isinstance(data, dict):
            self.logger.error("YAML 内容不是有效的字典结构")
            return None

        # 2. 解析为 SkillDSL
        try:
            skill = self.parser.parse(data)
        except Exception as e:
            self.logger.error(f"Skill 解析失败: {e}")
            return None

        # 3. 安全校验
        validation = self.validator.validate_all(skill, yaml_content)
        if not validation.passed:
            self.logger.error(f"安全校验失败: {validation.errors}")
            return None

        # 4. ID 冲突检测
        existing = self._find_in_marketplace(skill.skill_id)
        if existing and not force:
            self.logger.warning(f"Skill {skill.skill_id} 已存在，使用 force=True 覆盖")
            return None

        # 5. 设置市场元数据
        if not skill.market_meta:
            skill.market_meta = SkillMarketMeta()
        skill.market_meta.installed_at = datetime.now(timezone.utc).isoformat()

        # 6. 保存到 marketplace 目录
        self._save_to_marketplace(skill)

        # 7. 更新索引
        self._index[skill.skill_id] = {
            "name": skill.name,
            "category": skill.market_meta.category,
            "author": skill.author,
            "version": skill.version,
            "installed_at": skill.market_meta.installed_at,
            "source": "import",
        }
        self._save_index()

        self.logger.info(f"📥 导入 Skill: {skill.skill_id} ({skill.name})")
        return skill

    def import_from_file(self, file_path: str, force: bool = False) -> Optional[SkillDSL]:
        """从文件导入"""
        path = Path(file_path)
        if not path.exists():
            self.logger.error(f"文件不存在: {file_path}")
            return None
        with open(path, "r", encoding="utf-8") as f:
            return self.import_from_yaml(f.read(), force=force)

    def import_from_url(self, url: str, force: bool = False) -> Optional[SkillDSL]:
        """从 URL 导入（支持 GitHub raw、直链）"""
        import urllib.request
        import urllib.error

        # GitHub blob URL -> raw URL
        raw_url = self._normalize_url(url)

        try:
            req = urllib.request.Request(raw_url, headers={"User-Agent": "BlockMind/3.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError) as e:
            self.logger.error(f"下载失败: {url} -> {e}")
            return None

        skill = self.import_from_yaml(content, force=force)
        if skill and skill.market_meta:
            skill.market_meta.source_url = url
            self._save_to_marketplace(skill)
        return skill

    def import_from_bundle(self, bundle_dir: str) -> List[SkillDSL]:
        """从 Bundle 目录批量导入"""
        path = Path(bundle_dir)
        results = []
        for yaml_file in sorted(path.glob("*.yaml")):
            skill = self.import_from_file(str(yaml_file))
            if skill:
                results.append(skill)
        self.logger.info(f"📦 Bundle 导入: {len(results)} 个 Skill")
        return results

    # ── 安装/卸载 ──

    def install(self, skill_id: str) -> bool:
        """安装市场 Skill 到 custom 目录（激活）"""
        skill = self._find_in_marketplace(skill_id)
        if not skill:
            self.logger.error(f"安装失败: {skill_id} 不在市场中")
            return False

        # 复制到 custom
        src = self.marketplace_path / f"{skill_id}.yaml"
        dst = self.custom_path / f"{skill_id}.yaml"
        shutil.copy2(src, dst)

        # 更新索引
        if skill_id in self._index:
            self._index[skill_id]["installed"] = True
            self._save_index()

        # 通知 storage 刷新缓存
        if self.skill_storage:
            self.skill_storage._cache.pop(skill_id, None)

        self.logger.info(f"✅ 安装 Skill: {skill_id}")
        return True

    def uninstall(self, skill_id: str) -> bool:
        """从 custom 目录卸载（保留 marketplace 缓存）"""
        dst = self.custom_path / f"{skill_id}.yaml"
        if dst.exists():
            dst.unlink()

        # 更新索引
        if skill_id in self._index:
            self._index[skill_id]["installed"] = False
            self._save_index()

        # 通知 storage 刷新缓存
        if self.skill_storage:
            self.skill_storage._cache.pop(skill_id, None)

        self.logger.info(f"❌ 卸载 Skill: {skill_id}")
        return True

    def remove(self, skill_id: str) -> bool:
        """从市场完全移除（删除 marketplace 缓存 + custom）"""
        self.uninstall(skill_id)
        src = self.marketplace_path / f"{skill_id}.yaml"
        if src.exists():
            src.unlink()
        self._index.pop(skill_id, None)
        self._save_index()
        self.logger.info(f"🗑️ 移除 Skill: {skill_id}")
        return True

    # ── 浏览/搜索 ──

    def list_installed(self) -> List[dict]:
        """列出已安装的市场 Skill"""
        results = []
        for sid, meta in self._index.items():
            if meta.get("installed", True):
                results.append({"skill_id": sid, **meta})
        return results

    def list_available(self, category: str = None) -> List[dict]:
        """列出 marketplace 中可用的 Skill"""
        results = []
        for yaml_file in self.marketplace_path.glob("*.yaml"):
            try:
                skill = self.parser.parse_file(str(yaml_file))
                info = {
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "author": skill.author,
                    "version": skill.version,
                    "tags": skill.tags,
                    "task_level": skill.task_level,
                    "category": skill.market_meta.category if skill.market_meta else "general",
                    "description": skill.description,
                    "difficulty": skill.market_meta.difficulty if skill.market_meta else "beginner",
                    "rating": skill.market_meta.rating if skill.market_meta else 0,
                    "download_count": skill.market_meta.download_count if skill.market_meta else 0,
                    "installed": (self.custom_path / f"{skill.skill_id}.yaml").exists(),
                }
                if category and info["category"] != category:
                    continue
                results.append(info)
            except Exception:
                continue
        return results

    def search(self, query: str, category: str = None) -> List[dict]:
        """搜索市场 Skill"""
        results = []
        q = query.lower()
        for item in self.list_available(category):
            # 匹配 name, skill_id, tags, description
            searchable = " ".join([
                item.get("name", ""),
                item.get("skill_id", ""),
                " ".join(item.get("tags", [])),
                item.get("description", ""),
            ]).lower()
            if q in searchable:
                results.append(item)
        return results

    def get_detail(self, skill_id: str) -> Optional[dict]:
        """获取 Skill 详细信息"""
        skill = self._find_in_marketplace(skill_id)
        if not skill:
            return None
        return {
            "skill_id": skill.skill_id,
            "name": skill.name,
            "author": skill.author,
            "version": skill.version,
            "tags": skill.tags,
            "priority": skill.priority,
            "task_level": skill.task_level,
            "description": skill.description,
            "when": {"all": skill.when.all, "any": skill.when.any},
            "do_steps": [{"action": s.action, "args": s.args} for s in skill.do_steps],
            "until": {"any": skill.until.any},
            "market_meta": skill.market_meta.model_dump() if skill.market_meta else {},
            "installed": (self.custom_path / f"{skill_id}.yaml").exists(),
        }

    def get_stats(self) -> dict:
        """获取市场统计"""
        available = list(self.available_ids())
        installed = [
            sid for sid in available
            if (self.custom_path / f"{sid}.yaml").exists()
        ]
        categories = {}
        for sid in available:
            meta = self._index.get(sid, {})
            cat = meta.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1
        return {
            "total_available": len(available),
            "total_installed": len(installed),
            "categories": categories,
        }

    def available_ids(self) -> set:
        """获取 marketplace 中所有 skill_id"""
        ids = set()
        for yaml_file in self.marketplace_path.glob("*.yaml"):
            try:
                skill = self.parser.parse_file(str(yaml_file))
                ids.add(skill.skill_id)
            except Exception:
                continue
        return ids

    # ── 更新检测 ──

    def check_updates(self, registry_skills: List[dict]) -> List[dict]:
        """对比本地和注册中心，检测可更新的 Skill"""
        updates = []
        local_versions = {}
        for yaml_file in self.marketplace_path.glob("*.yaml"):
            try:
                skill = self.parser.parse_file(str(yaml_file))
                local_versions[skill.skill_id] = skill.version
            except Exception:
                continue

        for remote in registry_skills:
            sid = remote.get("skill_id", "")
            remote_ver = remote.get("version", 0)
            local_ver = local_versions.get(sid, 0)
            if sid in local_versions and remote_ver > local_ver:
                updates.append({
                    "skill_id": sid,
                    "name": remote.get("name", ""),
                    "local_version": local_ver,
                    "remote_version": remote_ver,
                })
        return updates

    # ── 内部方法 ──

    def _get_skill(self, skill_id: str) -> Optional[SkillDSL]:
        """获取 Skill（优先 custom，再 marketplace）"""
        # 先查 custom
        custom_file = self.custom_path / f"{skill_id}.yaml"
        if custom_file.exists():
            try:
                return self.parser.parse_file(str(custom_file))
            except Exception:
                pass
        # 再查 marketplace
        return self._find_in_marketplace(skill_id)

    def _find_in_marketplace(self, skill_id: str) -> Optional[SkillDSL]:
        """在 marketplace 目录查找 Skill"""
        path = self.marketplace_path / f"{skill_id}.yaml"
        if path.exists():
            try:
                return self.parser.parse_file(str(path))
            except Exception:
                pass
        return None

    def _save_to_marketplace(self, skill: SkillDSL) -> None:
        """保存 Skill 到 marketplace 目录"""
        path = self.marketplace_path / f"{skill.skill_id}.yaml"
        data = self._skill_to_export_dict(skill, include_meta=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    def _skill_to_export_dict(self, skill: SkillDSL, include_meta: bool = True) -> dict:
        """将 SkillDSL 转换为可导出的字典"""
        data = {
            "skill_id": skill.skill_id,
            "name": skill.name,
            "tags": skill.tags,
            "priority": skill.priority,
            "task_level": skill.task_level,
            "description": skill.description,
            "author": skill.author,
            "version": skill.version,
            "when": {"all": skill.when.all},
            "do": self._steps_to_do(skill.do_steps),
            "until": {"any": skill.until.any},
        }
        if include_meta and skill.market_meta:
            meta = skill.market_meta.model_dump(exclude_none=True)
            # 移除运行时字段
            for key in ("installed_at", "update_available"):
                meta.pop(key, None)
            if meta:
                data["market"] = meta
        return data

    def _steps_to_do(self, steps) -> list:
        """将 DoStep 列表转换为 YAML do 格式"""
        result = []
        for step in steps:
            if step.loop:
                loop_data = {}
                if step.loop.while_condition:
                    loop_data["while"] = step.loop.while_condition
                if step.loop.over_variable:
                    loop_data["over"] = step.loop.over_variable
                loop_data["do"] = self._steps_to_do(step.loop.do_steps)
                result.append({"loop": loop_data})
            elif step.condition:
                item = {"if": {"condition": step.condition}}
                if step.if_then:
                    item["if"]["then"] = self._steps_to_do(step.if_then)
                if step.if_else:
                    item["if"]["else"] = self._steps_to_do(step.if_else)
                result.append(item)
            elif step.action:
                entry = {"action": step.action}
                if step.args:
                    entry["args"] = step.args
                result.append(entry)
        return result

    @staticmethod
    def _normalize_url(url: str) -> str:
        """GitHub blob URL -> raw URL"""
        if "github.com" in url and "/blob/" in url:
            return url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        return url

    @staticmethod
    def compute_hash(content: str) -> str:
        """计算内容 SHA256"""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
