"""Skill 注册中心 — GitHub-based 社区 Skill 仓库"""
import json
import logging
import urllib.request
import urllib.error
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone


class SkillRegistry:
    """GitHub-based Skill 注册中心客户端"""

    DEFAULT_REPO = "bmbxwbh/blockmind-skills"
    RAW_BASE = "https://raw.githubusercontent.com"
    API_BASE = "https://api.github.com"

    def __init__(self, repo: str = None, token: str = None):
        self.repo = repo or self.DEFAULT_REPO
        self.token = token
        self.logger = logging.getLogger("blockmind.skill_registry")
        self._index_cache: Optional[dict] = None
        self._categories_cache: Optional[List[str]] = None

    # ── 索引 ──

    def fetch_index(self, force: bool = False) -> dict:
        """
        获取注册中心索引

        Returns:
            {
                "version": 1,
                "updated_at": "...",
                "categories": ["combat", "farming", ...],
                "skills": {
                    "skill_id": {
                        "name": "...", "author": "...", "version": 1,
                        "category": "...", "rating": 4.5, "downloads": 100,
                        "path": "combat/kill_mob.yaml"
                    }
                }
            }
        """
        if self._index_cache and not force:
            return self._index_cache

        try:
            content = self._fetch_file(".index.json")
            self._index_cache = json.loads(content)
            return self._index_cache
        except Exception as e:
            self.logger.warning(f"获取索引失败: {e}")
            # 返回空索引
            return {"version": 0, "skills": {}, "categories": []}

    def get_categories(self) -> List[str]:
        """获取所有分类"""
        if self._categories_cache:
            return self._categories_cache
        index = self.fetch_index()
        self._categories_cache = index.get("categories", [
            "combat", "farming", "building", "gathering",
            "navigation", "storage", "survival", "automation", "general"
        ])
        return self._categories_cache

    # ── 搜索/浏览 ──

    def search(self, query: str = "", category: str = None,
               sort: str = "popular", limit: int = 50) -> List[dict]:
        """
        搜索注册中心

        Args:
            query: 搜索关键词
            category: 分类筛选
            sort: 排序方式 (popular/newest/rating)
            limit: 返回数量

        Returns:
            Skill 列表
        """
        index = self.fetch_index()
        skills = index.get("skills", {})

        results = []
        for sid, meta in skills.items():
            # 分类筛选
            if category and meta.get("category") != category:
                continue
            # 关键词搜索
            if query:
                searchable = " ".join([
                    meta.get("name", ""),
                    sid,
                    " ".join(meta.get("tags", [])),
                    meta.get("description", ""),
                ]).lower()
                if query.lower() not in searchable:
                    continue
            results.append({"skill_id": sid, **meta})

        # 排序
        if sort == "popular":
            results.sort(key=lambda x: x.get("downloads", 0), reverse=True)
        elif sort == "newest":
            results.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        elif sort == "rating":
            results.sort(key=lambda x: x.get("rating", 0), reverse=True)

        return results[:limit]

    def get_skill_info(self, skill_id: str) -> Optional[dict]:
        """获取单个 Skill 的元数据"""
        index = self.fetch_index()
        skills = index.get("skills", {})
        if skill_id in skills:
            return {"skill_id": skill_id, **skills[skill_id]}
        return None

    # ── 获取内容 ──

    def fetch_skill_yaml(self, skill_id: str) -> Optional[str]:
        """获取 Skill 的 YAML 内容"""
        info = self.get_skill_info(skill_id)
        if not info:
            self.logger.error(f"Skill {skill_id} 不在注册中心")
            return None

        path = info.get("path", f"{skill_id}.yaml")
        try:
            return self._fetch_file(path)
        except Exception as e:
            self.logger.error(f"获取 Skill 内容失败: {e}")
            return None

    # ── 提交 ──

    def submit_skill(self, yaml_content: str, category: str = "general") -> dict:
        """
        提交 Skill 到注册中心（通过 GitHub API 创建 PR）

        Returns:
            {"success": bool, "pr_url": str, "message": str}
        """
        if not self.token:
            return {
                "success": False,
                "message": "需要 GitHub Token 才能提交。请配置 github_token。",
            }

        # 解析 YAML 获取 skill_id
        try:
            import yaml
            data = yaml.safe_load(yaml_content)
            skill_id = data.get("skill_id", "unknown")
            skill_name = data.get("name", skill_id)
        except Exception:
            return {"success": False, "message": "YAML 解析失败"}

        # 创建分支 + 提交文件 + 创建 PR
        try:
            branch = f"skill/{skill_id}"
            path = f"{category}/{skill_id}.yaml"

            # 1. 获取 main 的 SHA
            main_sha = self._gh_get_ref("heads/main")

            # 2. 创建分支
            self._gh_create_ref(f"refs/heads/{branch}", main_sha)

            # 3. 创建文件
            import base64
            content_b64 = base64.b64encode(yaml_content.encode("utf-8")).decode()
            self._gh_create_file(
                path=path,
                content_b64=content_b64,
                message=f"feat: add skill '{skill_name}' ({skill_id})",
                branch=branch,
            )

            # 4. 创建 PR
            pr = self._gh_create_pr(
                title=f"✨ 新增 Skill: {skill_name}",
                body=f"## 新增 Skill\n\n"
                     f"- **ID**: `{skill_id}`\n"
                     f"- **名称**: {skill_name}\n"
                     f"- **分类**: {category}\n"
                     f"- **作者**: {data.get('author', 'unknown')}\n\n"
                     f"```yaml\n{yaml_content[:500]}\n```",
                head=branch,
                base="main",
            )

            return {
                "success": True,
                "pr_url": pr.get("html_url", ""),
                "message": f"PR 已创建: {pr.get('html_url', '')}",
            }

        except Exception as e:
            self.logger.error(f"提交失败: {e}")
            return {"success": False, "message": f"提交失败: {e}"}

    # ── 统计 ──

    def record_download(self, skill_id: str) -> None:
        """记录下载（本地计数，定期同步到 Registry）"""
        # 本地记录，不阻塞
        pass

    def get_stats(self) -> dict:
        """获取注册中心统计"""
        index = self.fetch_index()
        skills = index.get("skills", {})
        categories = {}
        total_downloads = 0
        for meta in skills.values():
            cat = meta.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1
            total_downloads += meta.get("downloads", 0)
        return {
            "total_skills": len(skills),
            "total_downloads": total_downloads,
            "categories": categories,
            "repo": self.repo,
        }

    # ── 内部方法 ──

    def _fetch_file(self, path: str) -> str:
        """从 GitHub raw 获取文件内容"""
        url = f"{self.RAW_BASE}/{self.repo}/main/{path}"
        req = urllib.request.Request(url, headers={"User-Agent": "BlockMind/3.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8")

    def _gh_api(self, method: str, path: str, data: dict = None) -> dict:
        """调用 GitHub API"""
        url = f"{self.API_BASE}/repos/{self.repo}/{path}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "BlockMind/3.0",
        }
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())

    def _gh_get_ref(self, ref: str) -> str:
        """获取 Git ref SHA"""
        result = self._gh_api("GET", f"git/{ref}")
        return result["object"]["sha"]

    def _gh_create_ref(self, ref: str, sha: str) -> dict:
        """创建 Git ref"""
        return self._gh_api("POST", "git/refs", {"ref": ref, "sha": sha})

    def _gh_create_file(self, path: str, content_b64: str,
                        message: str, branch: str) -> dict:
        """创建/更新文件"""
        return self._gh_api("PUT", f"contents/{path}", {
            "message": message,
            "content": content_b64,
            "branch": branch,
        })

    def _gh_create_pr(self, title: str, body: str,
                      head: str, base: str) -> dict:
        """创建 Pull Request"""
        return self._gh_api("POST", "pulls", {
            "title": title,
            "body": body,
            "head": head,
            "base": base,
        })
