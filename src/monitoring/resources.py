"""System resource monitoring via psutil."""

import logging
import time
from typing import Dict, Any

import psutil

logger = logging.getLogger("blockmind.monitoring.resources")


def get_system_stats() -> Dict[str, Any]:
    """Collect current system resource statistics.

    Returns a dict with CPU, memory, disk, and network info,
    suitable for JSON serialization.
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=0)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
    except Exception:
        cpu_percent = 0.0
        cpu_count = 0
        cpu_freq = None

    try:
        mem = psutil.virtual_memory()
        memory = {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent,
        }
    except Exception:
        memory = {"total": 0, "available": 0, "used": 0, "percent": 0.0}

    try:
        swap = psutil.swap_memory()
        swap_info = {
            "total": swap.total,
            "used": swap.used,
            "free": swap.free,
            "percent": swap.percent,
        }
    except Exception:
        swap_info = {"total": 0, "used": 0, "free": 0, "percent": 0.0}

    try:
        disk = psutil.disk_usage("/")
        disk_info = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        }
    except Exception:
        disk_info = {"total": 0, "used": 0, "free": 0, "percent": 0.0}

    try:
        net = psutil.net_io_counters()
        network = {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
        }
    except Exception:
        network = {"bytes_sent": 0, "bytes_recv": 0, "packets_sent": 0, "packets_recv": 0}

    try:
        load_avg = list(psutil.getloadavg())
    except Exception:
        load_avg = [0.0, 0.0, 0.0]

    return {
        "cpu": {
            "percent": cpu_percent,
            "count": cpu_count,
            "freq_current": cpu_freq.current if cpu_freq else None,
            "freq_max": cpu_freq.max if cpu_freq and cpu_freq.max else None,
            "load_avg_1m": load_avg[0],
            "load_avg_5m": load_avg[1],
            "load_avg_15m": load_avg[2],
        },
        "memory": memory,
        "swap": swap_info,
        "disk": disk_info,
        "network": network,
        "timestamp": time.time(),
    }
