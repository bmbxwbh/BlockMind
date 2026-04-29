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
