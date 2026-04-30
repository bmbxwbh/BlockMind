"""操作 Agent — 无状态执行者，接收任务描述，决定执行策略

设计原则：
- 每次调用全新上下文，不保留历史
- 只注入：任务 + 游戏状态 + Skill 元数据 + DSL 参考
- 自主决定：用缓存 Skill / 生成新 Skill / 推理动作序列
- 完成后返回结果，上下文销毁
"""

import json
import logging
from typing import Dict, List, Optional, Any

from src.ai.provider import AIProvider
from src.ai.prompts import PROMPTS, DSL_SYNTAX_REFERENCE
from src.skills.models import SkillDSL
from src.skills.storage import SkillStorage
from src.skills.dsl_parser import DSLParser
from src.skills.validator import SkillValidator

logger = logging.getLogger("blockmind.operation_agent")


class OperationAgent:
    """操作 Agent — 无状态任务执行者

    职责：
    1. 接收干净的任务描述
    2. 查询是否有可用的缓存 Skill
    3. 有 → 直接返回 Skill 供执行
    4. 没有 → 生成新 Skill 或输出动作序列
    5. 返回结果后上下文销毁
    """

    def __init__(self, provider: AIProvider, skill_storage: SkillStorage):
        self.provider = provider
        self.skill_storage = skill_storage
        self.parser = DSLParser()
        self.validator = SkillValidator()

    async def execute(
        self,
        task: str,
        game_state: dict,
        skill_metadata: List[dict] = None,
    ) -> Dict[str, Any]:
        """执行任务

        Args:
            task: 干净的任务描述（主 Agent 已修饰）
            game_state: 当前游戏状态快照
            skill_metadata: 可用 Skill 元数据列表（名称+标签，不含完整 DSL）

        Returns:
            {
                "strategy": "cached_skill" | "new_skill" | "action_sequence",
                "skill": SkillDSL | None,
                "skill_id": str | None,
                "actions": list | None,
                "response": str,  # 给主 Agent 的简短结果描述
            }
        """
        # 1. 尝试匹配缓存 Skill
        cached = await self._try_match_skill(task, game_state)
        if cached:
            logger.info(f"命中缓存 Skill: {cached.skill_id}")
            return {
                "strategy": "cached_skill",
                "skill": cached,
                "skill_id": cached.skill_id,
                "actions": None,
                "response": f"使用缓存技能 [{cached.name}] 执行",
            }

        # 2. 无缓存，让 AI 决定策略
        return await self._ai_decide(task, game_state, skill_metadata or [])

    async def _try_match_skill(self, task: str, game_state: dict) -> Optional[SkillDSL]:
        """尝试从缓存中匹配 Skill"""
        all_skills = self.skill_storage.list_all()
        if not all_skills:
            return None

        # 构建匹配 prompt（极简，节省 token）
        skill_list = "\n".join([
            f"- {s.skill_id}: {s.name} [{','.join(s.tags)}]"
            for s in all_skills[:30]  # 最多30个
        ])

        prompt = f"""判断任务是否有匹配的已有技能。只输出技能 ID 或 "NONE"。

任务：{task}

已有技能：
{skill_list}

只输出一个技能 ID 或 NONE："""

        try:
            result = await self.provider.chat(
                [{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50,
            )
            result = result.strip().strip('"').strip("'")

            if result and result != "NONE":
                skill = self.skill_storage.get(result)
                if skill:
                    # 验证 when 条件
                    return skill
        except Exception as e:
            logger.warning(f"Skill 匹配失败: {e}")

        return None

    async def _ai_decide(
        self,
        task: str,
        game_state: dict,
        skill_metadata: List[dict],
    ) -> Dict[str, Any]:
        """AI 决定执行策略：生成 Skill 或输出动作序列"""

        skill_list = ""
        if skill_metadata:
            skill_list = "\n".join([
                f"- {s.get('name', '')}: {s.get('tags', [])}"
                for s in skill_metadata[:20]
            ])

        prompt = f"""你是 Minecraft 操作 Agent。根据任务决定执行策略。

## 任务
{task}

## 当前游戏状态
{self._format_state(game_state)}

## 决策规则
1. 如果任务是重复性操作（砍树、挖矿、种田等），生成 Skill DSL
2. 如果任务是一次性操作（走到某处、看一眼），输出动作序列
3. 如果任务太模糊，返回需要澄清的信息

{DSL_SYNTAX_REFERENCE}

## 输出格式（严格 JSON）
```json
{{
  "strategy": "skill" 或 "actions",
  "reason": "简短理由",
  "skill_id": "如果strategy=skill则填",
  "skill_yaml": "如果strategy=skill则填完整YAML",
  "actions": [
    {{"action": "walk_to", "x": 100, "y": 64, "z": -200}},
    {{"action": "dig_block", "x": 100, "y": 63, "z": -200}}
  ]
}}
```

只输出 JSON，不要解释。"""

        try:
            result = await self.provider.chat(
                [{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000,
            )
            result = result.strip()
            if result.startswith("```"):
                result = result.split("\n", 1)[1]
            if result.endswith("```"):
                result = result.rsplit("```", 1)[0]

            data = json.loads(result.strip())

            if data.get("strategy") == "skill" and data.get("skill_yaml"):
                # 解析并存储新 Skill
                try:
                    skill = self.parser.parse_yaml(data["skill_yaml"])
                    self.skill_storage.save(skill)
                    logger.info(f"生成新 Skill: {skill.skill_id}")
                    return {
                        "strategy": "new_skill",
                        "skill": skill,
                        "skill_id": skill.skill_id,
                        "actions": None,
                        "response": f"生成新技能 [{skill.name}] 并执行",
                    }
                except Exception as e:
                    logger.warning(f"Skill 解析失败: {e}，降级为动作序列")

            if data.get("actions"):
                return {
                    "strategy": "action_sequence",
                    "skill": None,
                    "skill_id": None,
                    "actions": data["actions"],
                    "response": f"执行 {len(data['actions'])} 个动作",
                }

        except Exception as e:
            logger.error(f"操作 Agent 决策失败: {e}")

        return {
            "strategy": "failed",
            "skill": None,
            "skill_id": None,
            "actions": None,
            "response": "无法理解任务，请重新描述",
        }

    @staticmethod
    def _format_state(state: dict) -> str:
        """格式化游戏状态为简洁字符串"""
        parts = []
        if "health" in state:
            parts.append(f"血量:{state['health']}")
        if "hunger" in state:
            parts.append(f"饥饿:{state['hunger']}")
        if "position" in state:
            p = state["position"]
            if isinstance(p, dict):
                parts.append(f"位置:({p.get('x',0):.0f},{p.get('y',0):.0f},{p.get('z',0):.0f})")
        if "dimension" in state:
            parts.append(f"维度:{state['dimension']}")
        if "weather" in state:
            parts.append(f"天气:{state['weather']}")
        return " | ".join(parts) if parts else "无状态信息"
