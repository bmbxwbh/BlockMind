"""空闲任务执行历史"""
import logging
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class IdleTaskRecord:
    """空闲任务执行记录"""
    task_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    duration_ms: int = 0
    details: str = ""


class IdleHistory:
    """空闲任务执行历史"""

    def __init__(self, max_records: int = 1000):
        self._records: List[IdleTaskRecord] = []
        self.max_records = max_records
        self.logger = logging.getLogger("blockmind.idle_history")

    def record(self, task_name: str, success: bool, duration_ms: int = 0, details: str = "") -> None:
        """记录执行结果"""
        entry = IdleTaskRecord(
            task_name=task_name,
            success=success,
            duration_ms=duration_ms,
            details=details,
        )
        self._records.append(entry)
        if len(self._records) > self.max_records:
            self._records = self._records[-self.max_records:]

    def get_stats(self) -> Dict[str, dict]:
        """获取统计信息"""
        stats = {}
        for record in self._records:
            if record.task_name not in stats:
                stats[record.task_name] = {"total": 0, "success": 0, "failed": 0}
            stats[record.task_name]["total"] += 1
            if record.success:
                stats[record.task_name]["success"] += 1
            else:
                stats[record.task_name]["failed"] += 1
        return stats

    def get_recent(self, limit: int = 50) -> List[IdleTaskRecord]:
        """获取最近的记录"""
        return self._records[-limit:]
