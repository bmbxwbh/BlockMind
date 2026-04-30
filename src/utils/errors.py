"""BlockMind 统一错误类与 FastAPI 异常处理器"""

from fastapi import Request
from fastapi.responses import JSONResponse


class BlockMindError(Exception):
    """BlockMind 基础异常"""

    code: str = "BLOCKMIND_ERROR"
    message: str = "An unexpected error occurred"
    hint: str = ""

    def __init__(self, message: str = "", hint: str = ""):
        self.message = message or self.__class__.message
        self.hint = hint or self.__class__.hint
        super().__init__(self.message)


class ConfigError(BlockMindError):
    """配置相关错误"""

    code = "CONFIG_ERROR"
    message = "Configuration error"
    hint = "Check your config file for invalid or missing values"


class ConnectionError(BlockMindError):
    """连接相关错误（Minecraft 服务器、外部服务等）"""

    code = "CONNECTION_ERROR"
    message = "Connection failed"
    hint = "Verify the target service is running and reachable"


class AIError(BlockMindError):
    """AI / LLM 调用错误"""

    code = "AI_ERROR"
    message = "AI service error"
    hint = "Check API key, model availability, and rate limits"


class SafetyError(BlockMindError):
    """安全策略违规"""

    code = "SAFETY_ERROR"
    message = "Safety policy violation"
    hint = "The requested action was blocked by the safety filter"


class SkillNotFoundError(BlockMindError):
    """技能未找到"""

    code = "SKILL_NOT_FOUND"
    message = "Skill not found"
    hint = "Check the skill name or install the required skill package"


# ---------------------------------------------------------------------------
# FastAPI exception handler
# ---------------------------------------------------------------------------

async def blockmind_error_handler(request: Request, exc: BlockMindError) -> JSONResponse:
    """将 BlockMindError 转换为统一 JSON 响应"""
    return JSONResponse(
        status_code=400,
        content={
            "error_code": exc.code,
            "message": exc.message,
            "hint": exc.hint,
        },
    )


def register_error_handlers(app) -> None:
    """在 FastAPI app 上注册所有 BlockMind 异常处理器"""
    app.add_exception_handler(BlockMindError, blockmind_error_handler)
