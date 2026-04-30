"""配置加载与校验"""
import yaml
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class GameReconnectConfig(BaseModel):
    enabled: bool = True
    interval: int = 5
    max_retries: int = -1


class ModWSBackoffConfig(BaseModel):
    """WebSocket auto-reconnect backoff settings."""
    initial_backoff: float = 2.0
    max_backoff: float = 120.0
    backoff_multiplier: float = 2.0


class ModConfig(BaseModel):
    """Mod connection configuration.

    Set no_mod_mode=true to skip Mod connection entirely
    (for standalone/testing mode without a Minecraft server).
    """
    host: str = "localhost"
    port: int = 25580
    timeout: float = 10.0
    no_mod_mode: bool = False
    expected_version: str = "1.1.0"
    bot_name: str = "BlockMind_Bot"
    ws_backoff: ModWSBackoffConfig = ModWSBackoffConfig()


class GameConfig(BaseModel):
    server_ip: str = "localhost"
    server_port: int = 25565
    username: str = "BlockMind"
    version: str = "1.20.4"
    auth_mode: str = "offline"
    reconnect: GameReconnectConfig = GameReconnectConfig()


class AgentConfig(BaseModel):
    """单个 Agent 的模型配置"""
    provider: str = "openai"
    api_key: str = ""
    model: str = "gpt-4o"
    base_url: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096
    fallback_models: List[str] = Field(default_factory=list)


class AIConfig(BaseModel):
    """AI 配置 — 双 Agent 架构"""
    # 主 Agent（玩家聊天，需要好的对话能力）
    main_agent: AgentConfig = AgentConfig(
        provider="openai",
        model="gpt-4o",
        temperature=0.7,
        max_tokens=512,
    )
    # 操作 Agent（任务执行，需要精准的代码生成能力）
    operation_agent: AgentConfig = AgentConfig(
        provider="openai",
        model="gpt-4o",
        temperature=0.3,
        max_tokens=4096,
    )
    # 兼容旧配置（如果只填了 ai.provider 等，两个 Agent 共用）
    provider: str = ""
    api_key: str = ""
    model: str = ""
    base_url: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096

    def get_main_agent(self) -> AgentConfig:
        """获取主 Agent 配置（优先用 main_agent，否则用顶层配置）"""
        if self.main_agent.api_key or self.provider:
            if not self.main_agent.api_key and self.api_key:
                return AgentConfig(
                    provider=self.provider or self.main_agent.provider,
                    api_key=self.api_key,
                    model=self.model or self.main_agent.model,
                    base_url=self.base_url or self.main_agent.base_url,
                    temperature=self.main_agent.temperature,
                    max_tokens=self.main_agent.max_tokens,
                    fallback_models=self.main_agent.fallback_models,
                )
            return self.main_agent
        return self.main_agent

    def get_operation_agent(self) -> AgentConfig:
        """获取操作 Agent 配置（优先用 operation_agent，否则用顶层配置）"""
        if self.operation_agent.api_key or self.provider:
            if not self.operation_agent.api_key and self.api_key:
                return AgentConfig(
                    provider=self.provider or self.operation_agent.provider,
                    api_key=self.api_key,
                    model=self.model or self.operation_agent.model,
                    base_url=self.base_url or self.operation_agent.base_url,
                    temperature=self.operation_agent.temperature,
                    max_tokens=self.operation_agent.max_tokens,
                    fallback_models=self.operation_agent.fallback_models,
                )
            return self.operation_agent
        return self.operation_agent


class SkillsValidationConfig(BaseModel):
    syntax_check: bool = True
    safety_check: bool = True
    logic_check: bool = True
    max_retries: int = 3


class SkillsVersioningConfig(BaseModel):
    enabled: bool = True
    max_versions: int = 10


class SkillsAutoRepairConfig(BaseModel):
    enabled: bool = True


class SkillsConfig(BaseModel):
    storage_path: str = "./skills"
    validation: SkillsValidationConfig = SkillsValidationConfig()
    auto_repair: SkillsAutoRepairConfig = SkillsAutoRepairConfig()
    versioning: SkillsVersioningConfig = SkillsVersioningConfig()


class SafetyAuditConfig(BaseModel):
    enabled: bool = True
    retention_days: int = 30


class SafetyAuthConfig(BaseModel):
    enabled: bool = True
    timeout: int = 30
    timeout_action: str = "deny"


class SafetyEmergencyConfig(BaseModel):
    enabled: bool = True
    auto_repair: bool = True


class SafetyConfig(BaseModel):
    audit_log: SafetyAuditConfig = SafetyAuditConfig()
    authorization: SafetyAuthConfig = SafetyAuthConfig()
    emergency_takeover: SafetyEmergencyConfig = SafetyEmergencyConfig()
    risk_levels: Optional[Dict[str, int]] = Field(default_factory=dict)


class MonitoringHealthConfig(BaseModel):
    enabled: bool = True
    interval: int = 10


class MonitoringFallbackConfig(BaseModel):
    retry_count: int = 3
    safe_point: str = "spawn"


class MonitoringAlertConfig(BaseModel):
    chat_notify: bool = True


class MonitoringConfig(BaseModel):
    health_check: MonitoringHealthConfig = MonitoringHealthConfig()
    fallback: MonitoringFallbackConfig = MonitoringFallbackConfig()
    alert: MonitoringAlertConfig = MonitoringAlertConfig()


class IdleTaskAction(BaseModel):
    name: str
    enabled: bool = True
    priority: int = 5


class IdleTasksConfig(BaseModel):
    enabled: bool = True
    interval: int = 30
    actions: List[IdleTaskAction] = Field(default_factory=lambda: [
        IdleTaskAction(name="farm_wheat"),
        IdleTaskAction(name="mine_resources"),
        IdleTaskAction(name="chop_tree"),
        IdleTaskAction(name="organize_chest"),
        IdleTaskAction(name="repair_building", priority=4),
        IdleTaskAction(name="place_torches", priority=4),
        IdleTaskAction(name="patrol_area", enabled=False),
        IdleTaskAction(name="deposit_items"),
    ])


class WebUIAuthConfig(BaseModel):
    enabled: bool = True
    password: str = "change-me"
    session_timeout: int = 3600


class WebUISecurityConfig(BaseModel):
    allow_remote: bool = True
    allowed_ips: List[str] = Field(default_factory=lambda: ["0.0.0.0/0"])


class WebUIConfig(BaseModel):
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 19951
    auth: WebUIAuthConfig = WebUIAuthConfig()
    security: WebUISecurityConfig = WebUISecurityConfig()


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str = "logs/companion.log"
    max_size: str = "100MB"
    backup_count: int = 5


class MemoryConfig(BaseModel):
    """记忆系统配置"""
    enabled: bool = True
    storage_path: str = "data/memory"
    auto_detect_zones: bool = True         # 自动检测建筑/危险/资源区域
    auto_detect_radius: int = 32           # 自动检测半径
    max_cached_paths: int = 500            # 最大缓存路径数
    max_strategies: int = 200              # 最大策略数
    path_success_threshold: float = 0.8    # 路径成功率阈值
    strategy_success_threshold: float = 0.6  # 策略成功率阈值
    protect_buildings: bool = True         # 建筑保护区自动保护


class NavigationConfig(BaseModel):
    """导航系统配置"""
    prefer_baritone: bool = True           # 优先使用 Baritone
    fallback_to_basic: bool = True         # Baritone 不可用时回退到基础寻路
    allow_break_default: bool = False      # 默认不允许破坏方块
    allow_place_default: bool = False      # 默认不允许放置方块
    sprint_default: bool = False           # 默认不疾跑
    max_path_length: int = 200             # 最大路径长度


class AppConfig(BaseModel):
    game: GameConfig = GameConfig()
    mod: ModConfig = ModConfig()
    ai: AIConfig = AIConfig()
    skills: SkillsConfig = SkillsConfig()
    safety: SafetyConfig = SafetyConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    idle_tasks: IdleTasksConfig = IdleTasksConfig()
    webui: WebUIConfig = WebUIConfig()
    logging: LoggingConfig = LoggingConfig()
    memory: MemoryConfig = MemoryConfig()
    navigation: NavigationConfig = NavigationConfig()


def load_config(path: str = "config.yaml") -> AppConfig:
    """加载 YAML 配置文件，返回 AppConfig 对象"""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")
    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return AppConfig(**raw)
