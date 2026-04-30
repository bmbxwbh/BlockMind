"""WebUI 认证模块"""

import hashlib
import hmac
import logging
import os
import secrets
import time
from typing import Optional

logger = logging.getLogger("blockmind.webui.auth")


class AuthManager:
    """WebUI 认证管理器

    支持密码登录和 Session Token 认证。
    """

    def __init__(self, password: str = "blockmind", session_timeout: int = 3600):
        # 优先读取环境变量
        env_password = os.environ.get("BLOCKMIND_PASSWORD")
        effective_password = env_password if env_password else password
        self.password_hash = self._hash_password(effective_password)
        self.session_timeout = session_timeout
        self._sessions: dict[str, float] = {}  # token → 创建时间

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        """验证密码"""
        return hmac.compare_digest(
            self._hash_password(password),
            self.password_hash,
        )

    def create_session(self) -> str:
        """创建会话 Token"""
        token = secrets.token_urlsafe(32)
        self._sessions[token] = time.time()
        logger.info("创建新会话")
        return token

    def verify_session(self, token: str) -> bool:
        """验证会话 Token"""
        if token not in self._sessions:
            return False
        created = self._sessions[token]
        if time.time() - created > self.session_timeout:
            del self._sessions[token]
            return False
        return True

    def invalidate_session(self, token: str) -> None:
        """注销会话"""
        self._sessions.pop(token, None)

    def cleanup_expired(self) -> int:
        """清理过期会话"""
        now = time.time()
        expired = [t for t, c in self._sessions.items() if now - c > self.session_timeout]
        for t in expired:
            del self._sessions[t]
        return len(expired)

    def get_token_from_header(self, authorization: Optional[str]) -> Optional[str]:
        """从 Authorization header 提取 token"""
        if authorization and authorization.startswith("Bearer "):
            return authorization[7:]
        return None
