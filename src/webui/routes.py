"""WebUI API 路由 — RESTful 接口"""

import logging
import time
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
import yaml

logger = logging.getLogger("blockmind.webui.routes")

_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config.yaml"


def save_config_to_yaml(config) -> None:
    """Read config.yaml, merge in-memory config changes, and write back."""
    if _CONFIG_PATH.exists():
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    # Build the ai section from in-memory config
    ai = data.setdefault("ai", {})

    def _agent_to_dict(agent_cfg):
        return {
            "provider": agent_cfg.provider,
            "api_key": agent_cfg.api_key,
            "model": agent_cfg.model,
            "base_url": agent_cfg.base_url or "",
            "temperature": agent_cfg.temperature,
            "max_tokens": agent_cfg.max_tokens,
        }

    ai["main_agent"] = _agent_to_dict(config.ai.get_main_agent())
    ai["operation_agent"] = _agent_to_dict(config.ai.get_operation_agent())

    with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

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

class SkillContentRequest(BaseModel):
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


@router.get("/api/skills/{skill_id}/content")
async def get_skill_content(skill_id: str, request: Request, _=Depends(require_auth)):
    """获取 Skill 的 YAML 内容"""
    engine = get_engine(request)
    if not hasattr(engine, 'skill_storage') or not engine.skill_storage:
        raise HTTPException(status_code=500, detail="Skill 存储未初始化")
    skill = engine.skill_storage.get(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill 未找到")
    # Serialize skill back to YAML-friendly dict
    content = {
        "skill_id": skill.skill_id,
        "name": skill.name,
        "tags": skill.tags,
        "priority": skill.priority,
        "task_level": skill.task_level,
        "when": {"all": skill.when.all, "any": skill.when.any},
        "do_steps": [{"action": s.action, "args": s.args} for s in skill.do_steps],
        "until": {"any": skill.until.any},
    }
    yaml_content = yaml.dump(content, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return {"skill_id": skill_id, "content": yaml_content}


@router.put("/api/skills/{skill_id}/content")
async def update_skill_content(skill_id: str, req: SkillContentRequest, request: Request, _=Depends(require_auth)):
    """更新 Skill 的 YAML 内容"""
    engine = get_engine(request)
    if not hasattr(engine, 'skill_storage') or not engine.skill_storage:
        raise HTTPException(status_code=500, detail="Skill 存储未初始化")
    # Validate YAML
    try:
        data = yaml.safe_load(req.content)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"YAML 解析错误: {e}")
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="YAML 根元素必须是字典")
    # Store the skill content (update via skill_storage if available)
    try:
        if hasattr(engine.skill_storage, 'update_from_yaml'):
            engine.skill_storage.update_from_yaml(skill_id, data)
        elif hasattr(engine.skill_storage, 'save'):
            engine.skill_storage.save(skill_id, data)
        return {"success": True, "message": f"Skill {skill_id} 已更新"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
async def get_audit_log(
    request: Request,
    _=Depends(require_auth),
    offset: int = 0,
    limit: int = 50,
):
    """获取审计日志"""
    engine = get_engine(request)
    if hasattr(engine, 'safety_gateway') and engine.safety_gateway:
        audit = getattr(engine.safety_gateway, '_audit', None)
        if audit:
            total = len(audit._entries)
            # Request enough from query to cover offset+limit
            all_entries = audit.query(limit=offset + limit)
            page = all_entries[offset:offset + limit]
            entries = [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "action": e.action,
                    "risk_level": e.risk_level,
                    "result": e.result,
                }
                for e in page
            ]
            return {
                "entries": entries,
                "pagination": {
                    "offset": offset,
                    "limit": limit,
                    "total": total,
                    "has_more": offset + limit < total,
                },
            }
    return {"entries": []}


# ── 系统接口 ──

@router.get("/api/system/health")
async def system_health(request: Request):
    """系统健康检查（无需认证）"""
    engine = request.app.state.engine
    components = {}
    # Mod 检查
    if hasattr(engine, 'mod_client') and engine.mod_client:
        components["mod"] = "ok" if getattr(engine.mod_client, 'is_connected', False) else "disconnected"
    else:
        components["mod"] = "unavailable"
    # AI 检查
    if hasattr(engine, 'main_agent') and engine.main_agent:
        components["ai"] = "ok" if hasattr(engine.main_agent, 'provider') else "not_configured"
    else:
        components["ai"] = "unavailable"
    # Memory 检查
    if hasattr(engine, 'memory') and engine.memory:
        components["memory"] = "ok"
    else:
        components["memory"] = "unavailable"
    return {
        "status": "ok",
        "service": "blockmind-webui",
        "version": "2.0.0",
        "uptime": int(time.time() - getattr(request.app.state, '_start_time', time.time())),
        "components": components,
    }


@router.get("/api/system/status")
async def system_status(request: Request, _=Depends(require_auth)):
    """系统状态"""
    engine = get_engine(request)
    mod_ok = False
    ai_ok = False
    if hasattr(engine, 'mod_client') and engine.mod_client:
        mod_ok = getattr(engine.mod_client, 'is_connected', False)
    if hasattr(engine, 'main_agent') and engine.main_agent:
        ai_ok = hasattr(engine.main_agent, 'provider') and engine.main_agent.provider is not None
    return {
        "mod_connected": mod_ok,
        "ai_connected": ai_ok,
        "webui_running": True,
    }


@router.get("/api/system/resources")
async def system_resources(request: Request, _=Depends(require_auth)):
    """获取系统资源使用情况（CPU、内存、磁盘、网络）"""
    from src.monitoring.resources import get_system_stats
    return get_system_stats()


# ── Token 统计接口 ──

@router.get("/api/stats/tokens")
async def token_stats(request: Request, _=Depends(require_auth)):
    """Token 使用统计"""
    engine = get_engine(request)

    # Aggregate stats from both providers
    main_stats = {}
    op_stats = {}
    if hasattr(engine, 'main_provider') and engine.main_provider:
        main_stats = engine.main_provider.token_tracker.get_stats()
    if hasattr(engine, 'op_provider') and engine.op_provider:
        op_stats = engine.op_provider.token_tracker.get_stats()

    # Combined totals
    combined = {
        "total_tokens_in": main_stats.get("total_tokens_in", 0) + op_stats.get("total_tokens_in", 0),
        "total_tokens_out": main_stats.get("total_tokens_out", 0) + op_stats.get("total_tokens_out", 0),
        "calls_count": main_stats.get("calls_count", 0) + op_stats.get("calls_count", 0),
        "cost_estimate": round(
            main_stats.get("cost_estimate", 0) + op_stats.get("cost_estimate", 0), 6
        ),
    }

    return {
        "combined": combined,
        "main_agent": main_stats,
        "operation_agent": op_stats,
    }


# ── 记忆系统接口 ──

class MemoryImportRequest(BaseModel):
    data: dict
    merge: bool = True


@router.get("/api/memory")
async def get_memory(request: Request, _=Depends(require_auth)):
    """获取记忆系统数据"""
    engine = get_engine(request)
    if not hasattr(engine, 'memory') or not engine.memory:
        return {"zones": [], "paths": [], "strategies": [], "players": []}

    mem = engine.memory
    zones = []
    for z in mem.zones.values():
        zones.append({
            "id": z.zone_id,
            "name": z.name,
            "type": z.zone_type.value,
            "center": z.center,
            "radius": z.radius,
        })

    paths = []
    for key, p in mem.paths.items():
        paths.append({
            "start": str(p.start),
            "end": str(p.end),
            "success_count": p.success_count,
            "fail_count": p.fail_count,
            "success_rate": p.success_rate,
        })

    strategies = []
    for key, s in mem.strategies.items():
        strategies.append({
            "task_type": s.task_type,
            "description": s.description,
            "success_count": s.success_count,
            "success_rate": s.success_rate,
        })

    players = []
    for name, p in mem.players.items():
        players.append({
            "name": p.player_name,
            "home": p.home_location,
            "interaction_count": p.interaction_count,
        })

    return {
        "zones": zones,
        "paths": paths,
        "strategies": strategies,
        "players": players,
        "stats": mem.get_stats(),
    }


@router.post("/api/memory/cleanup")
async def memory_cleanup(request: Request, _=Depends(require_auth)):
    """清理旧路径、低评分策略并压缩相似路径"""
    engine = get_engine(request)
    if not hasattr(engine, 'memory') or not engine.memory:
        raise HTTPException(status_code=500, detail="记忆系统未初始化")
    mem = engine.memory
    old_paths = mem.cleanup_old_paths()
    low_strats = mem.cleanup_low_scoring_strategies()
    compressed = mem.compress_similar_paths()
    return {
        "success": True,
        "removed_paths": old_paths,
        "removed_strategies": low_strats,
        "compressed_paths": compressed,
        "stats": mem.get_stats(),
    }


@router.get("/api/memory/export")
async def memory_export(request: Request, _=Depends(require_auth)):
    """导出全部记忆为 JSON"""
    engine = get_engine(request)
    if not hasattr(engine, 'memory') or not engine.memory:
        raise HTTPException(status_code=500, detail="记忆系统未初始化")
    return engine.memory.export_memory()


@router.post("/api/memory/import")
async def memory_import(req: MemoryImportRequest, request: Request, _=Depends(require_auth)):
    """导入记忆 JSON（支持合并或覆盖）"""
    engine = get_engine(request)
    if not hasattr(engine, 'memory') or not engine.memory:
        raise HTTPException(status_code=500, detail="记忆系统未初始化")
    stats = engine.memory.import_memory(req.data, merge=req.merge)
    return {"success": True, "imported": stats}


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

    def _mask_key(key: str) -> str:
        """Mask API key, returning only the last 4 characters."""
        if not key or len(key) <= 4:
            return "****" if key else ""
        return "*" * (len(key) - 4) + key[-4:]

    def agent_to_dict(agent_cfg):
        return {
            "provider": agent_cfg.provider,
            "model": agent_cfg.model,
            "base_url": agent_cfg.base_url or "",
            "temperature": agent_cfg.temperature,
            "max_tokens": agent_cfg.max_tokens,
            "has_key": bool(agent_cfg.api_key),
            "api_key_masked": _mask_key(agent_cfg.api_key),
        }

    return {
        "main_agent": agent_to_dict(config.ai.get_main_agent()),
        "operation_agent": agent_to_dict(config.ai.get_operation_agent()),
        "providers": ["openai", "anthropic"],
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
        if cfg.base_url is not None:
            config.ai.main_agent.base_url = cfg.base_url
        if cfg.temperature is not None:
            config.ai.main_agent.temperature = cfg.temperature
        if cfg.max_tokens is not None:
            config.ai.main_agent.max_tokens = cfg.max_tokens

    if req.operation_agent:
        cfg = req.operation_agent
        if cfg.provider:
            config.ai.operation_agent.provider = cfg.provider
        if cfg.api_key:
            config.ai.operation_agent.api_key = cfg.api_key
        if cfg.model:
            config.ai.operation_agent.model = cfg.model
        if cfg.base_url is not None:
            config.ai.operation_agent.base_url = cfg.base_url
        if cfg.temperature is not None:
            config.ai.operation_agent.temperature = cfg.temperature
        if cfg.max_tokens is not None:
            config.ai.operation_agent.max_tokens = cfg.max_tokens

    # 热更新 Provider
    try:
        from src.ai.provider import create_provider
        main_provider = create_provider(config.ai.get_main_agent())
        op_provider = create_provider(config.ai.get_operation_agent())
        engine.main_agent.provider = main_provider
        engine.operation_agent.provider = op_provider
        # 持久化到 config.yaml
        save_config_to_yaml(config)
        return {"success": True, "details": "模型配置已更新"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/api/config/model/test")
async def test_model_config(request: Request, _=Depends(require_auth)):
    """测试模型连接（带详细诊断）"""
    engine = get_engine(request)
    provider = engine.main_agent.provider
    config = engine.config.ai.get_main_agent()

    diagnostics = {
        "provider": config.provider,
        "model": config.model,
        "base_url": config.base_url or "(默认)",
        "has_key": bool(config.api_key),
    }

    try:
        result = await provider.chat(
            [{"role": "user", "content": "回复 OK"}],
            max_tokens=10,
        )
        return {"success": True, "response": result.strip(), "diagnostics": diagnostics}
    except Exception as e:
        error_msg = str(e)
        # 解析常见错误
        if "Invalid API key" in error_msg or "401" in error_msg:
            hint = "API Key 无效，请检查 Key 是否正确"
        elif "Cannot connect" in error_msg or "111" in error_msg:
            hint = f"无法连接到 {config.base_url}，请检查 URL 是否正确"
        elif "404" in error_msg:
            hint = f"模型 '{config.model}' 不存在，请检查模型名称"
        elif "429" in error_msg:
            hint = "请求过于频繁，请稍后重试"
        else:
            hint = "未知错误，请检查配置"
        diagnostics["error"] = error_msg
        diagnostics["hint"] = hint
        return {"success": False, "error": error_msg, "hint": hint, "diagnostics": diagnostics}


# ── 记忆备份接口 ──

@router.post("/api/memory/backup")
async def backup_memory(request: Request, _=Depends(require_auth)):
    """手动触发记忆备份"""
    engine = get_engine(request)
    if not hasattr(engine, 'memory') or not engine.memory:
        raise HTTPException(status_code=500, detail="记忆系统未初始化")
    path = engine.memory.backup()
    if path:
        return {"success": True, "path": path}
    return {"success": False, "error": "备份失败"}


@router.get("/api/memory/backups")
async def list_backups(request: Request, _=Depends(require_auth)):
    """获取备份列表"""
    engine = get_engine(request)
    if not hasattr(engine, 'memory') or not engine.memory:
        return {"backups": []}
    return {"backups": engine.memory.get_backup_list()}


# ── 任务队列接口 ──

@router.get("/api/tasks/queue")
async def task_queue(request: Request, _=Depends(require_auth)):
    """获取当前任务队列状态"""
    engine = get_engine(request)
    queue_info = {"pending": [], "running": [], "completed_count": 0, "failed_count": 0}
    if hasattr(engine, 'task_pool') and engine.task_pool:
        pool = engine.task_pool
        if hasattr(pool, 'pending_tasks'):
            queue_info["pending"] = [{"id": t.task_id, "name": t.name} for t in pool.pending_tasks[:20]]
        if hasattr(pool, 'active_task') and pool.active_task:
            queue_info["running"] = [{"id": pool.active_task.task_id, "name": pool.active_task.name}]
        queue_info["completed_count"] = getattr(pool, 'completed_count', 0)
        queue_info["failed_count"] = getattr(pool, 'failed_count', 0)
    return queue_info


# ── 命令面板接口 ──

class CommandPanelRequest(BaseModel):
    message: str


@router.post("/api/command/panel")
async def command_panel(req: CommandPanelRequest, request: Request, _=Depends(require_auth)):
    """命令面板 — 发送自然语言指令给 AI"""
    engine = get_engine(request)
    if not hasattr(engine, 'main_agent') or not engine.main_agent:
        raise HTTPException(status_code=500, detail="AI 未初始化")
    try:
        result = await engine.main_agent.chat(req.message)
        return {"success": True, "response": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── 对话历史接口 ──

@router.get("/api/chat/history")
async def chat_history(request: Request, limit: int = 50, _=Depends(require_auth)):
    """获取对话历史"""
    engine = get_engine(request)
    if hasattr(engine, 'chat_history'):
        return {"history": engine.chat_history[-limit:]}
    return {"history": []}


# ── Skill 市场接口 ──

class MarketplaceImportRequest(BaseModel):
    """市场导入请求"""
    content: str = ""           # YAML 内容
    url: str = ""               # 或 URL
    force: bool = False         # 强制覆盖

class MarketplaceSubmitRequest(BaseModel):
    """市场提交请求"""
    skill_id: str
    category: str = "general"

class MarketplaceInstallRequest(BaseModel):
    """市场安装请求"""
    skill_id: str

def _get_marketplace(request: Request):
    """获取市场管理器实例"""
    engine = get_engine(request)
    if not hasattr(engine, '_marketplace'):
        from src.skills.marketplace import SkillMarketplace
        storage_path = "./skills"
        if hasattr(engine, 'skill_storage') and engine.skill_storage:
            storage_path = str(engine.skill_storage.storage_path)
        engine._marketplace = SkillMarketplace(
            storage_path=storage_path,
            skill_storage=getattr(engine, 'skill_storage', None),
        )
    return engine._marketplace

def _get_registry(request: Request):
    """获取注册中心客户端"""
    engine = get_engine(request)
    if not hasattr(engine, '_registry'):
        from src.skills.registry import SkillRegistry
        engine._registry = SkillRegistry()
    return engine._registry


@router.get("/api/marketplace/browse")
async def marketplace_browse(
    request: Request,
    category: str = None,
    sort: str = "popular",
    _=Depends(require_auth),
):
    """浏览市场"""
    registry = _get_registry(request)
    marketplace = _get_marketplace(request)

    # 先从远程注册中心获取
    try:
        remote_skills = registry.search(category=category, sort=sort)
    except Exception as e:
        logger.warning(f"远程 Skill 注册中心查询失败: {e}")
        remote_skills = []

    # 合并本地 marketplace 数据
    local_skills = marketplace.list_available(category)
    local_ids = {s["skill_id"] for s in local_skills}

    # 远程的如果本地没有，添加到列表
    for rs in remote_skills:
        if rs["skill_id"] not in local_ids:
            rs["installed"] = False
            rs["source"] = "remote"
            local_skills.append(rs)

    return {
        "skills": local_skills,
        "categories": marketplace.CATEGORIES,
        "total": len(local_skills),
    }


@router.get("/api/marketplace/search")
async def marketplace_search(
    request: Request,
    q: str = "",
    category: str = None,
    _=Depends(require_auth),
):
    """搜索市场"""
    marketplace = _get_marketplace(request)
    registry = _get_registry(request)

    results = marketplace.search(q, category)

    # 补充远程结果
    try:
        remote = registry.search(q, category)
        local_ids = {r["skill_id"] for r in results}
        for rs in remote:
            if rs["skill_id"] not in local_ids:
                rs["source"] = "remote"
                results.append(rs)
    except Exception:
        pass

    return {"skills": results, "total": len(results)}


@router.get("/api/marketplace/stats")
async def marketplace_stats(request: Request, _=Depends(require_auth)):
    """获取市场统计"""
    marketplace = _get_marketplace(request)
    registry = _get_registry(request)

    local_stats = marketplace.get_stats()
    try:
        remote_stats = registry.get_stats()
    except Exception:
        remote_stats = {"total_skills": 0, "total_downloads": 0, "categories": {}}

    return {
        "local": local_stats,
        "remote": remote_stats,
    }


@router.get("/api/marketplace/{skill_id}")
async def marketplace_get_skill(skill_id: str, request: Request, _=Depends(require_auth)):
    """获取市场 Skill 详情"""
    marketplace = _get_marketplace(request)
    detail = marketplace.get_detail(skill_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Skill 未找到")
    return detail


@router.post("/api/marketplace/import")
async def marketplace_import(req: MarketplaceImportRequest, request: Request, _=Depends(require_auth)):
    """导入 Skill（从 YAML 或 URL）"""
    marketplace = _get_marketplace(request)

    if req.url:
        skill = marketplace.import_from_url(req.url, force=req.force)
    elif req.content:
        skill = marketplace.import_from_yaml(req.content, force=req.force)
    else:
        raise HTTPException(status_code=400, detail="需要提供 content 或 url")

    if not skill:
        raise HTTPException(status_code=400, detail="导入失败，请检查 YAML 内容或 URL")

    return {
        "success": True,
        "skill_id": skill.skill_id,
        "name": skill.name,
        "message": f"成功导入: {skill.name} ({skill.skill_id})",
    }


@router.post("/api/marketplace/{skill_id}/install")
async def marketplace_install(skill_id: str, request: Request, _=Depends(require_auth)):
    """安装市场 Skill 到本地"""
    marketplace = _get_marketplace(request)
    success = marketplace.install(skill_id)
    if not success:
        raise HTTPException(status_code=400, detail="安装失败")
    return {"success": True, "message": f"已安装: {skill_id}"}


@router.post("/api/marketplace/{skill_id}/uninstall")
async def marketplace_uninstall(skill_id: str, request: Request, _=Depends(require_auth)):
    """卸载市场 Skill"""
    marketplace = _get_marketplace(request)
    success = marketplace.uninstall(skill_id)
    return {"success": success, "message": f"已卸载: {skill_id}"}


@router.delete("/api/marketplace/{skill_id}")
async def marketplace_remove(skill_id: str, request: Request, _=Depends(require_auth)):
    """从市场完全移除"""
    marketplace = _get_marketplace(request)
    success = marketplace.remove(skill_id)
    return {"success": success, "message": f"已移除: {skill_id}"}


@router.post("/api/marketplace/{skill_id}/export")
async def marketplace_export(skill_id: str, request: Request, _=Depends(require_auth)):
    """导出 Skill 为 YAML"""
    marketplace = _get_marketplace(request)
    content = marketplace.export_skill(skill_id)
    if not content:
        raise HTTPException(status_code=404, detail="Skill 未找到")
    return {"skill_id": skill_id, "content": content}


@router.post("/api/marketplace/submit")
async def marketplace_submit(req: MarketplaceSubmitRequest, request: Request, _=Depends(require_auth)):
    """提交 Skill 到社区注册中心"""
    marketplace = _get_marketplace(request)
    registry = _get_registry(request)

    content = marketplace.export_skill(req.skill_id)
    if not content:
        raise HTTPException(status_code=404, detail="Skill 未找到")

    result = registry.submit_skill(content, category=req.category)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "提交失败"))

    return result


@router.get("/api/marketplace/updates/check")
async def marketplace_check_updates(request: Request, _=Depends(require_auth)):
    """检查更新"""
    marketplace = _get_marketplace(request)
    registry = _get_registry(request)

    try:
        remote_skills = registry.search(limit=200)
    except Exception:
        remote_skills = []

    updates = marketplace.check_updates(remote_skills)
    return {"updates": updates, "total": len(updates)}
