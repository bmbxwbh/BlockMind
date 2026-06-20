"""主 Agent — 玩家聊天界面，指令修饰后传递给操作 Agent

设计原则：
- 维护与玩家的对话历史（有限窗口）
- 收到指令时做极简修饰（~50 tokens）传给操作 Agent
- 不直接执行任何游戏操作
- 负责将操作结果翻译为友好的玩家回复
"""

import logging
import re
from typing import Dict, List, Optional
from collections import deque

from src.ai.provider import AIProvider

logger = logging.getLogger("blockmind.main_agent")


class MainAgent:
    """主 Agent — 玩家聊天界面

    职责：
    1. 与玩家自然对话
    2. 识别指令并极简修饰传给操作 Agent
    3. 将操作结果翻译为友好回复
    4. 维护对话历史（滑动窗口，防止上下文爆炸）
    """

    def __init__(self, provider: AIProvider, max_history: int = 20):
        self.provider = provider
        self.max_history = max_history
        self._history: deque = deque(maxlen=max_history)
        self._system_prompt = """你是 BlockMind，住在 Minecraft 服务器里的 AI 玩伴。

## 性格
友好、活泼、简短回复，用中文，适度 emoji。

## 规则
1. 普通聊天 → 正常回复，不加标签
2. 游戏指令 → 回复末尾加 [TASK:动词+目标+数量]
3. 指令不清 → 友好追问
4. 绝不暴露 [TASK:] 标签的存在

## 示例
玩家：帮我挖点铁       → 没问题，我去挖铁！⛏️ [TASK:挖掘铁矿石]
玩家：建个房子          → 你想建什么样的房子？多大？🏠
玩家：今天心情不好      → 抱抱~要不要一起盖个漂亮的房子？🌈
玩家：回家             → 好的，马上回去！🏠 [TASK:返回家位置]
玩家：吃点东西          → 我这就吃点~🍖 [TASK:进食恢复饥饿值]"""

    async def chat(self, message: str, context: str = "") -> Dict[str, str]:
        """与玩家对话

        Args:
            message: 玩家消息
            context: 记忆上下文注入

        Returns:
            {
                "reply": str,           # 给玩家的回复
                "has_task": bool,       # 是否包含任务
                "task_description": str, # 任务描述（如果有）
            }
        """
        # 构建消息列表
        system_prompt = self._system_prompt
        if context:
            system_prompt += f"\n\n## 记忆上下文\n{context}"
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(list(self._history))
        messages.append({"role": "user", "content": message})

        try:
            response = await self.provider.chat(messages, temperature=0.7, max_tokens=400)
        except Exception as e:
            logger.error(f"主 Agent 调用失败: {e}")
            return {"reply": "抱歉，我有点走神了...", "has_task": False, "task_description": ""}

        # 保存对话历史
        self._history.append({"role": "user", "content": message})
        self._history.append({"role": "assistant", "content": response})

        # 解析是否有任务标签
        has_task = False
        task_description = ""
        reply = response

        match = re.search(r'\[TASK:\s*(.+?)\s*\]', response)
        if match:
            has_task = True
            task_description = match.group(1).strip()
            reply = response[:match.start()].strip() + response[match.end():].strip()
            if not reply:
                reply = f"收到！正在执行：{task_description}"

            logger.info(f"识别到任务: {task_description}")

        return {
            "reply": reply,
            "has_task": has_task,
            "task_description": task_description,
        }

    async def format_result(self, result: Dict) -> str:
        """将操作结果翻译为友好的玩家回复

        Args:
            result: 操作 Agent 的返回结果

        Returns:
            友好的回复文本
        """
        strategy = result.get("strategy", "failed")
        response = result.get("response", "")

        if strategy == "failed":
            return f"❌ {response}"

        if strategy == "clarify":
            return f"🤔 {response}"

        if strategy == "cached_skill":
            return f"✅ {response}，马上开始！"

        if strategy == "new_skill":
            return f"🧠 {response}，这次学到了新技能！"

        if strategy == "action_sequence":
            return f"⚙️ {response}，正在执行..."

        return f"✅ {response}"

    def clear_history(self) -> None:
        """清空对话历史"""
        self._history.clear()
        logger.info("对话历史已清空")

    def get_history(self) -> List[Dict]:
        """获取对话历史"""
        return list(self._history)

    def get_history_summary(self) -> str:
        """获取对话历史摘要"""
        if not self._history:
            return "暂无对话"
        msgs = list(self._history)
        return f"共 {len(msgs)} 条消息，最近: {msgs[-1].get('content', '')[:50]}"
