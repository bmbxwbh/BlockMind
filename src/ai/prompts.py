"""Prompt 模板管理"""

PROMPTS = {
    "skill_generation": """你是一个 Minecraft AI 助手。将以下任务转换为 Skill DSL（YAML 格式）。
任务：{task_description}
游戏状态：{game_state}
可用函数：{available_functions}
要求：严格 YAML 语法，禁止硬编码坐标，必须含 when/do/until。只输出 YAML。""",

    "parameter_fill": """填充 Skill 参数。
任务：{task}
Skill：{skill_name}
游戏状态：{game_state}
返回 JSON 格式的参数。""",

    "template_fill": """填充 Skill 模板。
任务：{task}
模板：{template}
游戏状态：{game_state}
返回完整的 Skill DSL YAML。""",

    "emergency_takeover": """【紧急接管】直接控制 MC 机器人。
状态：{context_snapshot}
规则：只输出动作指令，优先：溺水>被攻击>掉落。
安全后输出 SAFE。""",

    "error_analysis": """分析 Skill 执行错误。
Skill：{skill_dsl}
错误：{error_message}
日志：{execution_log}
返回：根因 + 修复建议。""",

    "skill_repair": """修复 Skill DSL。
原始：{original_skill}
分析：{error_analysis}
返回修复后的完整 YAML。""",
}
