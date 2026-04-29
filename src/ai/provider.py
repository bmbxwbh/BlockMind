"""AI 提供商抽象层 — 统一调用接口"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, AsyncIterator
from src.config.loader import AIConfig


class AIProvider(ABC):
    """AI 提供商基类"""

    @abstractmethod
    async def chat(self, messages: List[Dict], temperature: float = 0.7,
                   max_tokens: int = 4096) -> str:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass


class OpenAIProvider(AIProvider):
    """OpenAI 适配器"""

    def __init__(self, config: AIConfig):
        self.config = config
        self.logger = logging.getLogger("blockmind.ai.openai")

    async def chat(self, messages, temperature=0.7, max_tokens=4096) -> str:
        import httpx
        base_url = self.config.base_url or "https://api.openai.com/v1"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.config.api_key}"},
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=60,
            )
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def health_check(self) -> bool:
        try:
            await self.chat([{"role": "user", "content": "ping"}], max_tokens=5)
            return True
        except Exception:
            return False


class AnthropicProvider(AIProvider):
    """Anthropic 适配器"""

    def __init__(self, config: AIConfig):
        self.config = config
        self.logger = logging.getLogger("blockmind.ai.anthropic")

    async def chat(self, messages, temperature=0.7, max_tokens=4096) -> str:
        import httpx
        base_url = self.config.base_url or "https://api.anthropic.com"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{base_url}/v1/messages",
                headers={
                    "x-api-key": self.config.api_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=60,
            )
            data = resp.json()
            return data["content"][0]["text"]

    async def health_check(self) -> bool:
        try:
            await self.chat([{"role": "user", "content": "ping"}], max_tokens=5)
            return True
        except Exception:
            return False


def create_provider(config: AIConfig) -> AIProvider:
    """工厂函数：根据配置创建 Provider"""
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }
    cls = providers.get(config.provider)
    if not cls:
        raise ValueError(f"不支持的 AI 提供商: {config.provider}")
    return cls(config)
