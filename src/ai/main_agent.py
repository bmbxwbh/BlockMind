"""主 Agent — 玩家聊天界面，指令修饰后传递给操作 Agent

设计原则：
- 维护与玩家的对话历史（有限窗口）
- 收到指令时做极简修饰（~50 tokens）传给操作 Agent
- 不直接执行任何游戏操作
- 负责将操作结果翻译为友好的玩家回复
"""

import logging
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
        self._system_prompt = """你是 BlockMind，一个住在 Minecraft 服务器里的智能 AI 玩伴。

## 你的性格
- 友好、活泼、偶尔卖萌
- 用中文交流
- 简短回复，不要长篇大论
- 会用 emoji 但不过度

## 你的能力
- 和玩家聊天
- 接收游戏指令（砍树、挖矿、建房子等）
- 执行指令并汇报结果

## 规则
- 如果玩家的话是普通聊天，正常回复
- 如果玩家的话是游戏指令，在回复前先输出内部标签 [TASK:任务描述]
- 任务描述要简洁明确，如 "挖掘铁矿石32个" "砍伐橡树收集木材"
- 不要在回复中暴露内部机制"""

    async def chat(self, message: str) -> Dict[str, str]:
        """与玩家对话

        Args:
            message: 玩家消息

        Returns:
            {
                "reply": str,           # 给玩家的回复
                "has_task": bool,       # 是否包含任务
                "task_description": str, # 任务描述（如果有）
            }
        """
        # 构建消息列表
        messages = [{"role": "system", "content": self._system_prompt}]
        messages.extend(list(self._history))
        messages.append({"role": "user", "content": message})

        try:
            response = await self.provider.chat(messages, temperature=0.7, max_tokens=200)
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

        if "[TASK:" in response:
            has_task = True
            # 提取任务描述
            start = response.index("[TASK:") + 6
            end = response.index("]", start) if "]" in response[start:] else len(response)
            task_description = response[start:end].strip()

            # 移除标签，只保留给玩家的回复
            reply = response[:response.index("[TASK:")].strip()
            if "]" in response[start:]:
                reply += response[end + 1:].strip()

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
