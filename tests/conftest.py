"""测试配置"""

import pytest


@pytest.fixture
def mock_mod_client():
    """Mock ModClient"""
    from unittest.mock import AsyncMock, MagicMock
    client = MagicMock()
    client.get_status = AsyncMock(return_value={
        "connected": True, "health": 20.0, "hunger": 20,
        "position": {"x": 0, "y": 64, "z": 0},
    })
    client.get_inventory = AsyncMock(return_value={"items": [], "empty_slots": 36, "is_full": False})
    client.get_entities = AsyncMock(return_value=[])
    client.get_blocks = AsyncMock(return_value=[])
    client.move = AsyncMock(return_value={"success": True, "details": "OK"})
    client.dig = AsyncMock(return_value={"success": True, "details": "OK"})
    client.chat = AsyncMock(return_value={"success": True, "details": "OK"})
    return client
