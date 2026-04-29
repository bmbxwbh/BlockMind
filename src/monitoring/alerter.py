"""告警通知器 — 按级别发送聊天框告警"""
import logging
from src.mod_client.client import ModClient


class Alerter:
    """告警通知器"""

    # MC 颜色代码
    LEVEL_FORMATS = {
        1: "§e[提示] ",      # 黄色
        2: "§6[警告] ",      # 金色
        3: "§c§l[紧急告警] ", # 红色加粗
    }

    def __init__(self, mod_client: ModClient = None):
        self.mod_client = mod_client
        self.logger = logging.getLogger("blockmind.alerter")
        self._alert_history = []

    async def alert(self, level: int, message: str) -> None:
        """发送告警"""
        prefix = self.LEVEL_FORMATS.get(level, "[通知] ")
        full_message = f"{prefix}{message}"

        # 日志
        log_msg = f"[L{level}] {message}"
        if level == 1:
            self.logger.info(log_msg)
        elif level == 2:
            self.logger.warning(log_msg)
        else:
            self.logger.error(log_msg)

        # 聊天框通知
        if self.mod_client:
            try:
                await self.mod_client.chat(full_message)
            except Exception as e:
                self.logger.error(f"发送告警失败: {e}")

        self._alert_history.append({"level": level, "message": message})

    async def info(self, message: str) -> None:
        """1级提示"""
        await self.alert(1, message)

    async def warning(self, message: str) -> None:
        """2级警告"""
        await self.alert(2, message)

    async def emergency(self, message: str) -> None:
        """3级紧急"""
        await self.alert(3, message)
