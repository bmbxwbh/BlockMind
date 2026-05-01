"""Skill DSL 数据模型"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class WhenClause(BaseModel):
    """触发条件"""
    all: List[str] = Field(default_factory=list)
    any: List[str] = Field(default_factory=list)


class DoStep(BaseModel):
    """执行步骤"""
    action: str = ""
    args: Dict[str, Any] = Field(default_factory=dict)
    loop: Optional['LoopBlock'] = None
    condition: Optional[str] = None
    if_then: Optional[List['DoStep']] = None
    if_else: Optional[List['DoStep']] = None


class LoopBlock(BaseModel):
    """循环块"""
    while_condition: Optional[str] = None
    over_variable: Optional[str] = None
    do_steps: List[DoStep] = Field(default_factory=list)
    max_iterations: int = 1000


class UntilClause(BaseModel):
    """结束条件"""
    any: List[str] = Field(default_factory=list)


class SkillDSL(BaseModel):
    """Skill DSL 完整结构"""
    skill_id: str
    name: str
    tags: List[str] = Field(default_factory=list)
    priority: int = 5
    when: WhenClause = WhenClause()
    do_steps: List[DoStep] = Field(default_factory=list)
    until: UntilClause = UntilClause()
    description: str = ""
    author: str = "system"
    version: int = 1
    usage_count: int = 0
    success_rate: float = 1.0
    task_level: str = "L2"  # L1/L2/L3
    market_meta: Optional['SkillMarketMeta'] = None


class SkillMarketMeta(BaseModel):
    """Skill 市场元数据"""
    category: str = "general"                # combat/farming/building/gathering/navigation/storage/survival/general
    difficulty: str = "beginner"             # beginner/intermediate/advanced
    mc_versions: List[str] = Field(default_factory=list)  # 兼容MC版本
    description_long: str = ""               # 详细描述（Markdown）
    source_url: str = ""                     # 来源URL
    homepage: str = ""                       # 项目主页
    license: str = "MIT"                     # 开源许可
    keywords: List[str] = Field(default_factory=list)  # 搜索关键词
    dependencies: List[str] = Field(default_factory=list)  # 依赖的其他 skill_id
    download_count: int = 0                  # 下载量
    rating: float = 0.0                      # 评分 0-5
    rating_count: int = 0                    # 评分人数
    created_at: str = ""                     # 创建时间 ISO
    updated_at: str = ""                     # 更新时间 ISO
    installed_at: Optional[str] = None       # 本地安装时间
    update_available: bool = False           # 是否有更新
    registry_version: int = 0                # 注册中心版本号（用于更新检测）


class SkillResult(BaseModel):
    """Skill 执行结果"""
    success: bool
    skill_id: str
    details: str = ""
    duration_ms: int = 0
    steps_completed: int = 0


class ValidationResult(BaseModel):
    """校验结果"""
    passed: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
