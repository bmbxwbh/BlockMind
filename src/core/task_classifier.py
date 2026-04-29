"""任务分类器 — 三维判断：步骤可预测性 / 输入复杂度 / 结果可验证性"""

import logging
from typing import Optional

logger = logging.getLogger("blockmind.task_classifier")


class TaskLevel:
    """任务级别常量"""
    L1_FIXED = "L1_fixed"            # 完全固定：步骤永远一样
    L2_PARAMETER = "L2_parameter"    # 参数化：步骤相同，目标不同
    L3_TEMPLATE = "L3_template"      # 模板化：结构类似，细节不同
    L4_DYNAMIC = "L4_dynamic"        # 完全动态：每次不同


class TaskClassifier:
    """任务分类器

    通过三维判断自动分类任务：
    1. 步骤是否可预测（每次相同？）
    2. 输入是否简单（≤3个参数？）
    3. 结果是否可验证（量化？）

    分类流程：
    1. 精确匹配已知固定任务库
    2. 精确匹配已知参数化任务库
    3. 关键词分析
    4. AI 辅助判断（兜底）
    """

    # 已知固定任务（精确匹配）
    FIXED_TASKS = {
        "吃东西": "eat_food",
        "进食": "eat_food",
        "整理箱子": "organize_chest",
        "存放物品": "deposit_items",
        "存东西": "deposit_items",
        "睡觉": "sleep",
        "回家": "go_home",
        "回安全点": "go_safe_point",
    }

    # 参数化任务（流程固定，目标不同）
    PARAMETERIZED_TASKS = {
        "砍树": "chop_tree",
        "挖矿": "mine_ore",
        "种田": "farm_wheat",
        "采集": "collect",
        "钓鱼": "fish",
        "杀怪": "kill_mob",
        "收集": "collect",
    }

    # 模板化任务关键词
    TEMPLATE_KEYWORDS = ["建墙", "铺路", "搭桥", "围栏", "围墙", "挖洞", "填平"]

    # 动态任务关键词
    DYNAMIC_KEYWORDS = ["建", "设计", "造", "装修", "规划", "布局", "探索", "打boss", "攻略"]

    # 固定任务关键词（用于模糊匹配）
    FIXED_KEYWORDS = ["吃", "睡", "存", "整理", "修补", "回去", "回家"]

    # 参数化任务关键词
    PARAM_KEYWORDS = ["砍", "挖", "种", "捡", "放", "采集", "收集", "钓鱼", "杀"]

    def classify(self, task: str) -> str:
        """分类任务

        Args:
            task: 自然语言任务描述

        Returns:
            "L1_fixed" / "L2_parameter" / "L3_template" / "L4_dynamic"
        """
        task = task.strip()

        # 1. 精确匹配已知固定任务
        if task in self.FIXED_TASKS:
            logger.debug(f"精确匹配 L1: {task}")
            return TaskLevel.L1_FIXED

        # 2. 精确匹配已知参数化任务
        if task in self.PARAMETERIZED_TASKS:
            logger.debug(f"精确匹配 L2: {task}")
            return TaskLevel.L2_PARAMETER

        # 3. 模板化任务关键词
        for kw in self.TEMPLATE_KEYWORDS:
            if kw in task:
                logger.debug(f"关键词匹配 L3: {task} (命中: {kw})")
                return TaskLevel.L3_TEMPLATE

        # 4. 动态任务关键词（优先级高于参数化，因为"建房子"包含"建"）
        for kw in self.DYNAMIC_KEYWORDS:
            if kw in task:
                logger.debug(f"关键词匹配 L4: {task} (命中: {kw})")
                return TaskLevel.L4_DYNAMIC

        # 5. 参数化任务关键词
        for kw in self.PARAM_KEYWORDS:
            if kw in task:
                logger.debug(f"关键词匹配 L2: {task} (命中: {kw})")
                return TaskLevel.L2_PARAMETER

        # 6. 固定任务关键词
        for kw in self.FIXED_KEYWORDS:
            if kw in task:
                logger.debug(f"关键词匹配 L1: {task} (命中: {kw})")
                return TaskLevel.L1_FIXED

        # 7. 兜底：默认为动态任务
        logger.debug(f"默认 L4: {task}")
        return TaskLevel.L4_DYNAMIC

    def classify_with_ai(self, task: str, ai_provider) -> str:
        """AI 辅助分类（用于关键词无法判断的情况）

        Args:
            task: 任务描述
            ai_provider: AI 提供商实例

        Returns:
            任务级别
        """
        prompt = f"""判断以下 Minecraft 任务的分类级别，只返回 L1/L2/L3/L4：

任务：{task}

L1=完全固定（步骤永远一样，如进食、存放物品、睡觉）
L2=参数化（流程固定但目标不同，如砍树、挖矿、种田）
L3=模板化（结构类似但细节不同，如建墙、铺路）
L4=完全动态（每次不同，如建房子、探索洞穴、打Boss）

只回答 L1、L2、L3 或 L4："""

        try:
            # 兼容同步和异步 AI provider
            import asyncio
            if asyncio.iscoroutinefunction(ai_provider.chat):
                result = asyncio.get_event_loop().run_until_complete(
                    ai_provider.chat([{"role": "user", "content": prompt}], max_tokens=10)
                )
            else:
                result = ai_provider.chat([{"role": "user", "content": prompt}], max_tokens=10)

            result = result.strip().upper()
            level_map = {"L1": TaskLevel.L1_FIXED, "L2": TaskLevel.L2_PARAMETER,
                         "L3": TaskLevel.L3_TEMPLATE, "L4": TaskLevel.L4_DYNAMIC}
            level = level_map.get(result)
            if level:
                logger.info(f"AI 分类: {task} → {level}")
                return level
        except Exception as e:
            logger.error(f"AI 分类失败: {e}")

        # 回退到关键词分类
        return self.classify(task)

    def get_task_skill_id(self, task: str) -> Optional[str]:
        """获取已知任务对应的 Skill ID"""
        if task in self.FIXED_TASKS:
            return self.FIXED_TASKS[task]
        if task in self.PARAMETERIZED_TASKS:
            return self.PARAMETERIZED_TASKS[task]
        return None
