"""WebUI FastAPI 应用 — BlockMind 控制面板"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from src.webui.routes import router
from src.webui.auth import AuthManager
from src.webui.websocket import WSManager

logger = logging.getLogger("blockmind.webui")


def create_app(engine=None, config=None) -> FastAPI:
    """创建 WebUI FastAPI 应用

    Args:
        engine: CompanionEngine 实例
        config: WebUIConfig 配置

    Returns:
        FastAPI 应用实例
    """
    app = FastAPI(
        title="BlockMind 控制面板",
        description="Minecraft AI 玩伴管理界面",
        version="2.0.0",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 初始化管理器
    auth_config = config.auth if config else None
    app.state.auth_manager = AuthManager(
        password=auth_config.password if auth_config else "blockmind",
        session_timeout=auth_config.session_timeout if auth_config else 3600,
    )
    app.state.ws_manager = WSManager(
        event_bus=engine.event_bus if engine else None,
    )
    app.state.engine = engine

    # 注册路由
    app.include_router(router)

    # 静态文件
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # 前端入口
    @app.get("/", response_class=HTMLResponse)
    async def index():
        template = Path(__file__).parent / "templates" / "index.html"
        if template.exists():
            return template.read_text(encoding="utf-8")
        return "<h1>BlockMind 控制面板</h1><p>前端文件未找到</p>"

    # WebSocket 端点
    @app.websocket("/ws")
    async def websocket_endpoint(ws):
        await engine.state.ws_manager.connect(ws)
        try:
            while True:
                data = await ws.receive_text()
                # 客户端消息暂不处理
        except Exception:
            app.state.ws_manager.disconnect(ws)

    @app.on_event("startup")
    async def startup():
        logger.info("WebUI 启动")
        app.state.ws_manager.start_event_listener()

    @app.on_event("shutdown")
    async def shutdown():
        logger.info("WebUI 关闭")

    return app
