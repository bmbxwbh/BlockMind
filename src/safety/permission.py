"""权限管理器"""
import logging
from typing import Set


class PermissionManager:
    """操作权限管理"""

    def __init__(self):
        self._allowed: Set[str] = set()
        self._denied: Set[str] = set()
        self.logger = logging.getLogger("blockmind.permission")

    def is_allowed(self, action: str) -> bool:
        if action in self._denied:
            return False
        return action in self._allowed or not self._allowed

    def is_denied(self, action: str) -> bool:
        return action in self._denied

    def allow(self, action: str) -> None:
        self._allowed.add(action)
        self._denied.discard(action)

    def deny(self, action: str) -> None:
        self._denied.add(action)
        self._allowed.discard(action)

    def reset(self) -> None:
        self._allowed.clear()
        self._denied.clear()
