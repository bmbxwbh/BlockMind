"""BlockMind — 智能 Minecraft AI 玩伴系统 主入口"""
import asyncio
import signal
import sys
from src.config.loader import load_config
from src.core.engine import CompanionEngine
from src.utils.logger import setup_logger


async def main():
    """主入口函数"""
    config = load_config("config.yaml")
    logger = setup_logger(config.logging)
    logger.info("🎮 BlockMind 启动中...")
    logger.info(f"   MC 服务器: {config.game.server_ip}:{config.game.server_port}")
    logger.info(f"   AI 模型: {config.ai.provider}/{config.ai.model}")
    logger.info(f"   WebUI: {'开启' if config.webui.enabled else '关闭'}")

    engine = CompanionEngine(config)

    # 优雅退出
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(engine.shutdown()))

    # 启动 WebUI（如果启用）
    webui_task = None
    if config.webui.enabled:
        import uvicorn
        from src.webui.app import create_app
        app = create_app(engine=engine, config=config.webui)
        webui_config = uvicorn.Config(
            app,
            host=config.webui.host,
            port=config.webui.port,
            log_level="info",
        )
        webui_server = uvicorn.Server(webui_config)
        webui_task = asyncio.create_task(webui_server.serve())
        logger.info(f"🌐 WebUI 启动于 http://{config.webui.host}:{config.webui.port}")

    # 启动引擎
    engine_task = asyncio.create_task(engine.start())

    # 等待任一任务完成（优雅退出时）
    await asyncio.gather(engine_task, webui_task)


if __name__ == "__main__":
    asyncio.run(main())
