"""配置加载与校验"""
import yaml
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class GameReconnectConfig(BaseModel):
    enabled: bool = True
    interval: int = 5
    max_retries: int = -1


class GameConfig(BaseModel):
    server_ip: str = "localhost"
    server_port: int = 25565
    username: str = "BlockMind"
    version: str = "1.20.4"
    auth_mode: str = "offline"
    reconnect: GameReconnectConfig = GameReconnectConfig()


class AIThinkingConfig(BaseModel):
    enabled: bool = True
    max_tokens: int = 8192


class AIConfig(BaseModel):
    provider: str = "openai"
    api_key: str = ""
    model: str = "gpt-4o"
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = True
    thinking: AIThinkingConfig = AIThinkingConfig()


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
    port: int = 8080
    auth: WebUIAuthConfig = WebUIAuthConfig()
    security: WebUISecurityConfig = WebUISecurityConfig()


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str = "logs/companion.log"
    max_size: str = "100MB"
    backup_count: int = 5


class AppConfig(BaseModel):
    game: GameConfig = GameConfig()
    ai: AIConfig = AIConfig()
    skills: SkillsConfig = SkillsConfig()
    safety: SafetyConfig = SafetyConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    idle_tasks: IdleTasksConfig = IdleTasksConfig()
    webui: WebUIConfig = WebUIConfig()
    logging: LoggingConfig = LoggingConfig()


def load_config(path: str = "config.yaml") -> AppConfig:
    """加载 YAML 配置文件，返回 AppConfig 对象"""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")
    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return AppConfig(**raw)
