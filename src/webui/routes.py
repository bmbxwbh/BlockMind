"""WebUI API 路由 — RESTful 接口"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

logger = logging.getLogger("blockmind.webui.routes")

router = APIRouter()


# ── 请求/响应模型 ──

class LoginRequest(BaseModel):
    password: str

class LoginResponse(BaseModel):
    token: str
    expires_in: int

class CommandRequest(BaseModel):
    command: str
    args: str = ""

class SkillEditRequest(BaseModel):
    skill_id: str
    content: str

class ConfigUpdateRequest(BaseModel):
    section: str
    key: str
    value: str


# ── 认证中间件 ──

def get_auth_manager(request: Request):
    return request.app.state.auth_manager

def get_engine(request: Request):
    return request.app.state.engine


async def require_auth(request: Request):
    """认证依赖"""
    auth = request.app.state.auth_manager
    token = auth.get_token_from_header(request.headers.get("Authorization"))
    if not token or not auth.verify_session(token):
        raise HTTPException(status_code=401, detail="未认证")
    return token


# ── 认证接口 ──

@router.post("/api/login", response_model=LoginResponse)
async def login(req: LoginRequest, request: Request):
    """登录获取 Token"""
    auth = request.app.state.auth_manager
    if not auth.verify_password(req.password):
        raise HTTPException(status_code=401, detail="密码错误")
    token = auth.create_session()
    return LoginResponse(token=token, expires_in=auth.session_timeout)


@router.post("/api/logout")
async def logout(request: Request, token: str = Depends(require_auth)):
    """注销"""
    auth = request.app.state.auth_manager
    auth.invalidate_session(token)
    return {"success": True}


# ── 仪表盘接口 ──

@router.get("/api/dashboard")
async def dashboard(request: Request, _=Depends(require_auth)):
    """仪表盘数据"""
    engine = get_engine(request)
    status = {
        "connected": False,
        "health": 0,
        "hunger": 0,
        "position": {"x": 0, "y": 0, "z": 0},
        "dimension": "unknown",
        "tasks_running": 0,
        "skills_count": 0,
        "uptime": 0,
    }

    # 尝试获取 Mod 状态
    if hasattr(engine, 'mod_client') and engine.mod_client:
        try:
            player = await engine.mod_client.get_status()
            status.update({
                "connected": player.connected,
                "health": player.health,
                "hunger": player.hunger,
                "position": player.position,
                "dimension": player.dimension,
                "weather": player.weather,
                "time_of_day": player.time_of_day,
            })
        except Exception as e:
            logger.warning(f"获取状态失败: {e}")

    return status


# ── Skill 管理接口 ──

@router.get("/api/skills")
async def list_skills(request: Request, _=Depends(require_auth), category: str = None):
    """列出所有 Skill"""
    engine = get_engine(request)
    if hasattr(engine, 'skill_storage') and engine.skill_storage:
        skills = engine.skill_storage.list_all(category)
        return {"skills": [
            {
                "skill_id": s.skill_id,
                "name": s.name,
                "tags": s.tags,
                "priority": s.priority,
                "task_level": s.task_level,
                "usage_count": s.usage_count,
                "success_rate": s.success_rate,
            }
            for s in skills
        ]}
    return {"skills": []}


@router.get("/api/skills/{skill_id}")
async def get_skill(skill_id: str, request: Request, _=Depends(require_auth)):
    """获取单个 Skill 详情"""
    engine = get_engine(request)
    if hasattr(engine, 'skill_storage') and engine.skill_storage:
        skill = engine.skill_storage.get(skill_id)
        if skill:
            return {
                "skill_id": skill.skill_id,
                "name": skill.name,
                "tags": skill.tags,
                "priority": skill.priority,
                "when": {"all": skill.when.all, "any": skill.when.any},
                "do_steps": [{"action": s.action, "args": s.args} for s in skill.do_steps],
                "until": {"any": skill.until.any},
                "task_level": skill.task_level,
                "usage_count": skill.usage_count,
                "success_rate": skill.success_rate,
            }
    raise HTTPException(status_code=404, detail="Skill 未找到")


@router.delete("/api/skills/{skill_id}")
async def delete_skill(skill_id: str, request: Request, _=Depends(require_auth)):
    """删除 Skill"""
    engine = get_engine(request)
    if hasattr(engine, 'skill_storage') and engine.skill_storage:
        engine.skill_storage.delete(skill_id)
        return {"success": True}
    raise HTTPException(status_code=500, detail="Skill 存储未初始化")


# ── 安全设置接口 ──

@router.get("/api/safety/config")
async def get_safety_config(request: Request, _=Depends(require_auth)):
    """获取安全配置"""
    engine = get_engine(request)
    return {
        "enabled": True,
        "risk_levels": {},
        "auth_timeout": 30,
    }


@router.get("/api/safety/audit")
async def get_audit_log(request: Request, _=Depends(require_auth), limit: int = 50):
    """获取审计日志"""
    engine = get_engine(request)
    if hasattr(engine, 'safety_gateway') and engine.safety_gateway:
        audit = getattr(engine.safety_gateway, '_audit', None)
        if audit:
            entries = audit.query(limit=limit)
            return {"entries": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "action": e.action,
                    "risk_level": e.risk_level,
                    "result": e.result,
                }
                for e in entries
            ]}
    return {"entries": []}


# ── 系统接口 ──

@router.get("/api/system/health")
async def system_health(request: Request):
    """系统健康检查（无需认证）"""
    return {"status": "ok", "service": "blockmind-webui"}


@router.get("/api/system/status")
async def system_status(request: Request, _=Depends(require_auth)):
    """系统状态"""
    engine = get_engine(request)
    return {
        "mod_connected": getattr(engine, 'mod_client', None) is not None,
        "ai_connected": getattr(engine, 'ai_provider', None) is not None,
        "webui_running": True,
    }


@router.post("/api/command")
async def execute_command(req: CommandRequest, request: Request, _=Depends(require_auth)):
    """执行远程指令"""
    engine = get_engine(request)
    # 通过事件总线分发指令
    if hasattr(engine, 'event_bus') and engine.event_bus:
        from src.core.event_bus import Event
        await engine.event_bus.emit(Event(
            type=f"command.{req.command}",
            data={"args": req.args, "source": "webui"},
            source="webui",
        ))
        return {"success": True, "details": f"指令已发送: {req.command}"}
    return {"success": False, "error": "引擎未初始化"}


# ── 模型配置接口 ──

class AgentConfigUpdate(BaseModel):
    provider: str = ""
    api_key: str = ""
    model: str = ""
    base_url: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096


class ModelConfigUpdate(BaseModel):
    main_agent: Optional[AgentConfigUpdate] = None
    operation_agent: Optional[AgentConfigUpdate] = None


@router.get("/api/config/model")
async def get_model_config(request: Request, _=Depends(require_auth)):
    """获取当前模型配置"""
    engine = get_engine(request)
    config = engine.config

    def agent_to_dict(agent_cfg):
        return {
            "provider": agent_cfg.provider,
            "model": agent_cfg.model,
            "base_url": agent_cfg.base_url or "",
            "temperature": agent_cfg.temperature,
            "max_tokens": agent_cfg.max_tokens,
            "has_key": bool(agent_cfg.api_key),
        }

    return {
        "main_agent": agent_to_dict(config.ai.get_main_agent()),
        "operation_agent": agent_to_dict(config.ai.get_operation_agent()),
        "providers": ["openai", "anthropic", "deepseek", "openrouter", "mimo", "local"],
    }


@router.post("/api/config/model")
async def update_model_config(req: ModelConfigUpdate, request: Request, _=Depends(require_auth)):
    """更新模型配置（热更新，无需重启）"""
    engine = get_engine(request)
    config = engine.config

    if req.main_agent:
        cfg = req.main_agent
        if cfg.provider:
            config.ai.main_agent.provider = cfg.provider
        if cfg.api_key:
            config.ai.main_agent.api_key = cfg.api_key
        if cfg.model:
            config.ai.main_agent.model = cfg.model
        if cfg.base_url:
            config.ai.main_agent.base_url = cfg.base_url
        if cfg.temperature != 0.7:
            config.ai.main_agent.temperature = cfg.temperature
        if cfg.max_tokens != 4096:
            config.ai.main_agent.max_tokens = cfg.max_tokens

    if req.operation_agent:
        cfg = req.operation_agent
        if cfg.provider:
            config.ai.operation_agent.provider = cfg.provider
        if cfg.api_key:
            config.ai.operation_agent.api_key = cfg.api_key
        if cfg.model:
            config.ai.operation_agent.model = cfg.model
        if cfg.base_url:
            config.ai.operation_agent.base_url = cfg.base_url
        if cfg.temperature != 0.7:
            config.ai.operation_agent.temperature = cfg.temperature
        if cfg.max_tokens != 4096:
            config.ai.operation_agent.max_tokens = cfg.max_tokens

    # 热更新 Provider
    try:
        from src.ai.provider import create_provider
        main_provider = create_provider(config.ai.get_main_agent())
        op_provider = create_provider(config.ai.get_operation_agent())
        engine.main_agent.provider = main_provider
        engine.operation_agent.provider = op_provider
        return {"success": True, "details": "模型配置已更新"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/api/config/model/test")
async def test_model_config(request: Request, _=Depends(require_auth)):
    """测试模型连接"""
    engine = get_engine(request)
    try:
        result = await engine.main_agent.provider.chat(
            [{"role": "user", "content": "回复 OK"}],
            max_tokens=10,
        )
        return {"success": True, "response": result.strip()}
    except Exception as e:
        return {"success": False, "error": str(e)}
