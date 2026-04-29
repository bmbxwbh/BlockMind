"""聊天交互 — 处理玩家指令和系统消息"""

import logging
import re
from typing import Optional, Callable, Dict, List
from dataclasses import dataclass

from src.core.event_bus import EventBus, Event
from src.mod_client.client import ModClient

logger = logging.getLogger("blockmind.chat")


@dataclass
class ChatCommand:
    """聊天指令"""
    raw: str           # 原始消息
    prefix: str = ""   # 指令前缀 (!)
    command: str = ""  # 指令名称
    args: str = ""     # 指令参数
    player: str = ""   # 发送者


class ChatHandler:
    """聊天交互处理器

    监听玩家聊天消息，解析指令（!stop, !come 等），触发回调。
    """

    COMMAND_PREFIX = "!"

    # 预定义系统指令
    SYSTEM_COMMANDS = {
        "stop": "终止所有任务",
        "come": "传送到玩家身边",
        "safe": "回安全点",
        "status": "查看状态",
        "approve": "同意高风险操作",
        "deny": "拒绝高风险操作",
        "disable_ai": "禁用 AI 接管",
        "enable_ai": "启用 AI 接管",
        "help": "查看指令列表",
    }

    def __init__(self, event_bus: EventBus, mod_client: ModClient):
        self.event_bus = event_bus
        self.mod_client = mod_client
        self._command_handlers: Dict[str, Callable] = {}
        self._chat_filters: List[Callable] = []

        # 监听聊天事件
        self.event_bus.subscribe("chat", self._on_chat)

    def register_command(self, command: str, handler: Callable) -> None:
        """注册指令处理器"""
        self._command_handlers[command] = handler
        logger.info(f"注册指令: {self.COMMAND_PREFIX}{command}")

    def add_chat_filter(self, filter_fn: Callable) -> None:
        """添加聊天消息过滤器"""
        self._chat_filters.append(filter_fn)

    async def _on_chat(self, event: Event) -> None:
        """处理聊天事件"""
        player = event.data.get("player", "")
        message = event.data.get("message", "")

        # 过滤器
        for f in self._chat_filters:
            if not f(player, message):
                return

        # 解析指令
        cmd = self.parse_command(message, player)
        if cmd:
            logger.info(f"玩家指令: {player} → {cmd.command} {cmd.args}")
            await self._dispatch_command(cmd)
        else:
            logger.debug(f"普通消息: {player}: {message}")

    def parse_command(self, message: str, player: str = "") -> Optional[ChatCommand]:
        """解析聊天指令"""
        message = message.strip()
        if not message.startswith(self.COMMAND_PREFIX):
            return None

        parts = message[len(self.COMMAND_PREFIX):].split(maxsplit=1)
        command = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        return ChatCommand(
            raw=message,
            prefix=self.COMMAND_PREFIX,
            command=command,
            args=args,
            player=player,
        )

    async def _dispatch_command(self, cmd: ChatCommand) -> None:
        """分发指令到对应处理器"""
        # 优先使用注册的处理器
        if cmd.command in self._command_handlers:
            try:
                await self._command_handlers[cmd.command](cmd)
            except Exception as e:
                logger.error(f"指令执行失败 [{cmd.command}]: {e}")
                await self.send_system_message(f"§c指令执行失败: {e}")
        elif cmd.command in self.SYSTEM_COMMANDS:
            # 内置指令通过事件总线分发
            await self.event_bus.emit(Event(
                type=f"command.{cmd.command}",
                data={"args": cmd.args, "player": cmd.player},
                source="chat_handler",
            ))
        else:
            await self.send_system_message(f"§e未知指令: {cmd.command}，输入 !help 查看帮助")

    async def send_system_message(self, message: str) -> None:
        """发送系统消息到聊天"""
        await self.mod_client.chat(message)

    async def send_help(self) -> None:
        """发送帮助信息"""
        lines = ["§6§l=== BlockMind 指令 ==="]
        for cmd, desc in self.SYSTEM_COMMANDS.items():
            lines.append(f"§e!{cmd} §7- {desc}")
        for cmd in self._command_handlers:
            if cmd not in self.SYSTEM_COMMANDS:
                lines.append(f"§e!{cmd} §7- 自定义指令")
        await self.send_system_message("\n".join(lines))
