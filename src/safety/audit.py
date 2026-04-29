"""审计日志"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class AuditEntry:
    timestamp: datetime
    action: str
    risk_level: int
    result: str
    details: Dict = field(default_factory=dict)


class AuditLogger:
    """审计日志"""

    def __init__(self, max_entries: int = 10000):
        self._entries: List[AuditEntry] = []
        self.max_entries = max_entries
        self.logger = logging.getLogger("blockmind.audit")

    def log(self, action: str, risk_level: int, result: str, details: dict = None) -> None:
        entry = AuditEntry(
            timestamp=datetime.now(),
            action=action,
            risk_level=risk_level,
            result=result,
            details=details or {},
        )
        self._entries.append(entry)
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries:]
        self.logger.info(f"[审计] {action} 风险={risk_level} 结果={result}")

    def query(self, start_time=None, end_time=None, level=None, limit=100) -> List[AuditEntry]:
        results = self._entries
        if level is not None:
            results = [e for e in results if e.risk_level == level]
        if start_time:
            results = [e for e in results if e.timestamp >= start_time]
        if end_time:
            results = [e for e in results if e.timestamp <= end_time]
        return results[-limit:]
