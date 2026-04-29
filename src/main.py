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

    await engine.start()


if __name__ == "__main__":
    asyncio.run(main())
