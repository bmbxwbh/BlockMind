"""AI 提供商抽象层 — 统一调用接口，支持双 Agent 配置"""

import json
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional, Tuple, AsyncIterator
from src.ai.token_tracker import TokenTracker, UsageInfo, ChatResult

logger = logging.getLogger("blockmind.ai.provider")

# ── Retry / Fallback configuration ──
MAX_RETRIES = 3
BASE_DELAY = 1.0  # seconds


class AIConfig:
    """AI 配置（兼容旧代码）"""
    def __init__(self, provider: str = "openai", api_key: str = "",
                 model: str = "gpt-4o", base_url: str = "",
                 temperature: float = 0.7, max_tokens: int = 4096,
                 fallback_models: Optional[List[str]] = None,
                 **kwargs: Any) -> None:
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.fallback_models = fallback_models or []


class AIProvider(ABC):
    """AI 提供商基类"""

    def __init__(self) -> None:
        self.token_tracker: TokenTracker = TokenTracker()

    @abstractmethod
    async def chat(self, messages: List[Dict], temperature: float = 0.7,
                   max_tokens: int = 4096, stream: bool = False) -> ChatResult:
        pass

    async def chat_with_retry(self, messages: List[Dict], temperature: float = 0.7,
                              max_tokens: int = 4096, stream: bool = False) -> ChatResult:
        """Call chat with exponential backoff retry (MAX_RETRIES attempts)."""
        last_exc: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
                return await self.chat(messages, temperature=temperature,
                                       max_tokens=max_tokens, stream=stream)
            except Exception as exc:
                last_exc = exc
                if attempt < MAX_RETRIES - 1:
                    delay = BASE_DELAY * (2 ** attempt)
                    logger.warning("Attempt %d/%d failed (%s), retrying in %.1fs",
                                   attempt + 1, MAX_RETRIES, exc, delay)
                    await asyncio.sleep(delay)
        raise last_exc  # type: ignore[misc]

    async def chat_stream(self, messages: List[Dict], temperature: float = 0.7,
                          max_tokens: int = 4096) -> AsyncIterator[str]:
        """Streaming variant that yields text chunks.

        Default implementation delegates to chat(stream=True) which collects
        all chunks — concrete providers should override for true streaming.
        """
        result = await self.chat(messages, temperature=temperature,
                                 max_tokens=max_tokens, stream=True)
        yield str(result)

    async def health_check(self) -> bool:
        try:
            await self.chat([{"role": "user", "content": "ping"}], max_tokens=5)
            return True
        except Exception:
            return False


class OpenAIProvider(AIProvider):
    """OpenAI 兼容适配器（支持所有 OpenAI 格式 API）"""

    def __init__(self, config: AIConfig) -> None:
        super().__init__()
        self.config = config
        self.base_url = (config.base_url or "https://api.openai.com/v1").rstrip("/")
        self.logger = logging.getLogger("blockmind.ai.openai")
        self._provider_name = "openai"

    async def chat(self, messages: List[Dict], temperature: float = 0.7,
                   max_tokens: int = 4096, stream: bool = False) -> ChatResult:
        if stream:
            chunks = []
            async for chunk in self.chat_stream(messages, temperature=temperature,
                                                max_tokens=max_tokens):
                chunks.append(chunk)
            return ChatResult("".join(chunks))

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
            text = data["choices"][0]["message"]["content"]
            usage_data = data.get("usage", {})
            usage = UsageInfo(
                tokens_in=usage_data.get("prompt_tokens", 0),
                tokens_out=usage_data.get("completion_tokens", 0),
                model=self.config.model,
                provider=self._provider_name,
            )
            self.token_tracker.record(usage)
            return ChatResult(text, usage)

    async def chat_stream(self, messages: List[Dict], temperature: float = 0.7,
                          max_tokens: int = 4096) -> AsyncIterator[str]:
        """Yield text chunks via OpenAI SSE streaming."""
        import httpx
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
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
                    "stream": True,
                },
                timeout=httpx.Timeout(120, read=300),
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    payload = line[len("data: "):]
                    if payload.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(payload)
                        delta = chunk["choices"][0].get("delta", {})
                        text = delta.get("content")
                        if text:
                            yield text
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue


class AnthropicProvider(AIProvider):
    """Anthropic 适配器"""

    def __init__(self, config: AIConfig) -> None:
        super().__init__()
        self.config = config
        self.base_url = (config.base_url or "https://api.anthropic.com").rstrip("/")
        self._provider_name = "anthropic"

    def _build_body(self, messages: List[Dict], temperature: float,
                    max_tokens: int, stream: bool = False) -> Dict:
        """Separate system messages from chat messages (Anthropic requirement)."""
        system_msg = ""
        chat_messages = []
        for m in messages:
            if m["role"] == "system":
                system_msg += m["content"] + "\n"
            else:
                chat_messages.append(m)

        body: Dict[str, Any] = {
            "model": self.config.model,
            "messages": chat_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_msg.strip():
            body["system"] = system_msg.strip()
        if stream:
            body["stream"] = True
        return body

    async def chat(self, messages: List[Dict], temperature: float = 0.7,
                   max_tokens: int = 4096, stream: bool = False) -> ChatResult:
        if stream:
            chunks = []
            async for chunk in self.chat_stream(messages, temperature=temperature,
                                                max_tokens=max_tokens):
                chunks.append(chunk)
            return ChatResult("".join(chunks))

        import httpx
        body = self._build_body(messages, temperature, max_tokens)

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
            text = data["content"][0]["text"]
            usage_data = data.get("usage", {})
            usage = UsageInfo(
                tokens_in=usage_data.get("input_tokens", 0),
                tokens_out=usage_data.get("output_tokens", 0),
                model=self.config.model,
                provider=self._provider_name,
            )
            self.token_tracker.record(usage)
            return ChatResult(text, usage)

    async def chat_stream(self, messages: List[Dict], temperature: float = 0.7,
                          max_tokens: int = 4096) -> AsyncIterator[str]:
        """Yield text chunks via Anthropic SSE streaming."""
        import httpx
        body = self._build_body(messages, temperature, max_tokens, stream=True)

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/messages",
                headers={
                    "x-api-key": self.config.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=httpx.Timeout(120, read=300),
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    try:
                        event = json.loads(line[len("data: "):])
                    except json.JSONDecodeError:
                        continue
                    if event.get("type") == "content_block_delta":
                        delta = event.get("delta", {})
                        if delta.get("type") == "text_delta":
                            yield delta.get("text", "")
                    elif event.get("type") == "message_stop":
                        break


# ── 工厂函数 ──

_PROVIDER_MAP = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
}


class FallbackProvider(AIProvider):
    """Wraps a primary provider with fallback models.

    Tries the primary provider first (with retries), then falls back to
    alternate models in order, each also retried.
    """

    def __init__(self, primary: AIProvider, fallbacks: List[AIProvider],
                 primary_model: str) -> None:
        super().__init__()
        self.primary = primary
        self.fallbacks = fallbacks
        self.primary_model = primary_model
        self._fb_logger = logging.getLogger("blockmind.ai.fallback")

    async def chat(self, messages: List[Dict], temperature: float = 0.7,
                   max_tokens: int = 4096, stream: bool = False) -> ChatResult:
        providers = [self.primary] + self.fallbacks
        last_exc: Optional[Exception] = None
        for provider in providers:
            try:
                return await provider.chat_with_retry(
                    messages, temperature=temperature,
                    max_tokens=max_tokens, stream=stream)
            except Exception as exc:
                model = getattr(provider, 'config', None)
                model_name = getattr(model, 'model', 'unknown') if model else 'unknown'
                last_exc = exc
                self._fb_logger.warning("Provider (model=%s) exhausted retries: %s",
                                        model_name, exc)
        raise last_exc  # type: ignore[misc]


def create_provider(config: Any) -> AIProvider:
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
    primary = cls(cfg)

    # If fallback models configured, wrap in FallbackProvider
    if cfg.fallback_models:
        fallbacks: List[AIProvider] = []
        for fb_model in cfg.fallback_models:
            fb_cfg = AIConfig(
                provider=cfg.provider,
                api_key=cfg.api_key,
                model=fb_model,
                base_url=cfg.base_url,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
            fallbacks.append(cls(fb_cfg))
        logger.info("Fallback chain: %s -> %s", cfg.model,
                     " -> ".join(cfg.fallback_models))
        return FallbackProvider(primary, fallbacks, cfg.model)
    return primary


def create_dual_providers(config: Any) -> Tuple[AIProvider, AIProvider]:
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
        fallback_models=config.main_agent.fallback_models,
    )
    op_cfg = AIConfig(
        provider=config.operation_agent.provider,
        api_key=config.operation_agent.api_key,
        model=config.operation_agent.model,
        base_url=config.operation_agent.base_url,
        temperature=config.operation_agent.temperature,
        max_tokens=config.operation_agent.max_tokens,
        fallback_models=config.operation_agent.fallback_models,
    )
    return create_provider(main_cfg), create_provider(op_cfg)
