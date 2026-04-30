"""AI 提供商抽象层 — 统一调用接口，支持双 Agent 配置"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, AsyncIterator

logger = logging.getLogger("blockmind.ai.provider")


class AIConfig:
    """AI 配置（兼容旧代码）"""
    def __init__(self, provider="openai", api_key="", model="gpt-4o",
                 base_url="", temperature=0.7, max_tokens=4096, **kwargs):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens


class AIProvider(ABC):
    """AI 提供商基类"""

    @abstractmethod
    async def chat(self, messages: List[Dict], temperature: float = 0.7,
                   max_tokens: int = 4096) -> str:
        pass

    async def health_check(self) -> bool:
        try:
            await self.chat([{"role": "user", "content": "ping"}], max_tokens=5)
            return True
        except Exception:
            return False


class OpenAIProvider(AIProvider):
    """OpenAI 兼容适配器（支持所有 OpenAI 格式 API）"""

    def __init__(self, config: AIConfig):
        self.config = config
        self.base_url = (config.base_url or "https://api.openai.com/v1").rstrip("/")
        self.logger = logging.getLogger("blockmind.ai.openai")

    async def chat(self, messages, temperature=0.7, max_tokens=4096) -> str:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]


class AnthropicProvider(AIProvider):
    """Anthropic 适配器"""

    def __init__(self, config: AIConfig):
        self.config = config
        self.base_url = (config.base_url or "https://api.anthropic.com").rstrip("/")

    async def chat(self, messages, temperature=0.7, max_tokens=4096) -> str:
        import httpx
        # 转换消息格式（Anthropic 需要 system 单独传）
        system_msg = ""
        chat_messages = []
        for m in messages:
            if m["role"] == "system":
                system_msg += m["content"] + "\n"
            else:
                chat_messages.append(m)

        body = {
            "model": self.config.model,
            "messages": chat_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_msg.strip():
            body["system"] = system_msg.strip()

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/v1/messages",
                headers={
                    "x-api-key": self.config.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"]


# ── 工厂函数 ──

_PROVIDER_MAP = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    # 兼容别名
    "deepseek": OpenAIProvider,
    "openrouter": OpenAIProvider,
    "mimo": OpenAIProvider,
    "local": OpenAIProvider,
}


def create_provider(config) -> AIProvider:
    """工厂函数：根据配置创建 Provider

    Args:
        config: AIConfig 对象或具有相同属性的 Pydantic model
    """
    # 兼容 Pydantic model 和普通对象
    if hasattr(config, "model_dump"):
        cfg = AIConfig(**config.model_dump())
    elif isinstance(config, dict):
        cfg = AIConfig(**config)
    else:
        cfg = config

    provider_name = cfg.provider.lower()
    cls = _PROVIDER_MAP.get(provider_name)
    if not cls:
        raise ValueError(f"不支持的 AI 提供商: {cfg.provider}，支持: {list(_PROVIDER_MAP.keys())}")
    return cls(cfg)


def create_dual_providers(config) -> tuple:
    """创建双 Agent 的 Provider

    Args:
        config: 包含 main_agent 和 operation_agent 配置

    Returns:
        (main_provider, operation_provider)
    """
    main_cfg = AIConfig(
        provider=config.main_agent.provider,
        api_key=config.main_agent.api_key,
        model=config.main_agent.model,
        base_url=config.main_agent.base_url,
        temperature=config.main_agent.temperature,
        max_tokens=config.main_agent.max_tokens,
    )
    op_cfg = AIConfig(
        provider=config.operation_agent.provider,
        api_key=config.operation_agent.api_key,
        model=config.operation_agent.model,
        base_url=config.operation_agent.base_url,
        temperature=config.operation_agent.temperature,
        max_tokens=config.operation_agent.max_tokens,
    )
    return create_provider(main_cfg), create_provider(op_cfg)
