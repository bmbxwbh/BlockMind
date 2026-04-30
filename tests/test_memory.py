"""记忆系统 + 智能导航测试"""

import json
import os
import shutil
import tempfile
import pytest

from src.core.memory import (
    GameMemory, Zone, ZoneType,
    CachedPath, StrategyRecord, PlayerMemory, WorldMemory,
)


class TestMemorySystem:
    """记忆系统核心测试"""

    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.memory = GameMemory(storage_path=self.test_dir)

    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # ── 空间记忆 ──

    def test_add_zone(self):
        zone = Zone(
            zone_id="test_base", name="基地", zone_type=ZoneType.BASE,
            center=(100, 64, 200), radius=30, breakable=False,
        )
        self.memory.add_zone(zone)
        assert "test_base" in self.memory.zones
        assert self.memory.zones["test_base"].name == "基地"

    def test_zone_contains(self):
        zone = Zone(
            zone_id="test", name="test", zone_type=ZoneType.BUILDING,
            center=(100, 64, 200), radius=10,
        )
        assert zone.contains(105, 64, 205) is True
        assert zone.contains(200, 64, 200) is False

    def test_register_building(self):
        zone = self.memory.register_building("主城", (100, 64, 200), radius=20)
        assert zone.zone_type == ZoneType.BUILDING
        assert zone.breakable is False
        assert zone.placeable is False

    def test_register_base(self):
        zone = self.memory.register_base("家", (50, 64, -100))
        assert zone.zone_type == ZoneType.BASE
        assert zone.breakable is False
        assert zone.placeable is True  # 基地内可以放置

    def test_register_danger(self):
        zone = self.memory.register_danger("岩浆湖", (80, 12, -50), "lava")
        assert zone.zone_type == ZoneType.DANGER
        assert self.memory.is_in_danger_zone(80, 12, -50) is True
        assert self.memory.is_in_danger_zone(0, 64, 0) is False

    def test_protection_zones(self):
        self.memory.register_building("主城", (100, 64, 200), radius=20)
        self.memory.register_resource("矿洞", (200, 12, 300))
        protections = self.memory.get_protection_zones()
        assert len(protections) == 1
        assert protections[0].name == "主城"

    def test_is_in_protected_zone(self):
        self.memory.register_building("主城", (100, 64, 200), radius=20)
        assert self.memory.is_in_protected_zone(105, 64, 205) is True
        assert self.memory.is_in_protected_zone(0, 64, 0) is False

    def test_get_nearby_zones(self):
        self.memory.register_building("A", (100, 64, 200))
        self.memory.register_building("B", (110, 64, 210))
        self.memory.register_building("C", (500, 64, 500))
        nearby = self.memory.get_nearby_zones(100, 64, 200, radius=30)
        assert len(nearby) == 2

    def test_remove_zone(self):
        self.memory.register_building("test", (100, 64, 200))
        assert self.memory.remove_zone("building_test") is True
        assert self.memory.remove_zone("nonexistent") is False

    def test_visit_zone(self):
        self.memory.register_building("test", (100, 64, 200))
        self.memory.visit_zone("building_test")
        zone = self.memory.get_zone("building_test")
        assert zone.visit_count == 1

    # ── 路径记忆 ──

    def test_cache_path(self):
        start = (0, 64, 0)
        end = (100, 64, 200)
        waypoints = [(0, 64, 0), (50, 64, 100), (100, 64, 200)]
        path = self.memory.cache_path(start, end, waypoints, success=True, duration=15.0)
        assert path.success_count == 1
        assert path.success_rate == 1.0

    def test_path_success_rate(self):
        start = (0, 64, 0)
        end = (100, 64, 200)
        self.memory.cache_path(start, end, [], success=True)
        self.memory.cache_path(start, end, [], success=True)
        self.memory.cache_path(start, end, [], success=False)
        path = self.memory.get_cached_path(start, end)
        assert path.success_rate == pytest.approx(2 / 3)

    def test_reliable_paths(self):
        # 可靠路径：成功率 > 80% 且至少成功 2 次
        self.memory.cache_path((0, 64, 0), (100, 64, 200), [], success=True)
        self.memory.cache_path((0, 64, 0), (100, 64, 200), [], success=True)
        self.memory.cache_path((0, 64, 0), (100, 64, 200), [], success=True)
        reliable = self.memory.get_reliable_paths()
        assert len(reliable) == 1

    def test_blacklist_path(self):
        start = (0, 64, 0)
        end = (100, 64, 200)
        self.memory.cache_path(start, end, [], success=False)
        self.memory.blacklist_path(start, end, "岩浆阻挡")
        path = self.memory.get_cached_path(start, end)
        assert path.is_reliable is False

    def test_get_paths_from(self):
        self.memory.cache_path((0, 64, 0), (100, 64, 200), [], success=True)
        self.memory.cache_path((0, 64, 0), (200, 64, 300), [], success=True)
        paths = self.memory.get_paths_from((0, 64, 0))
        assert len(paths) == 2

    # ── 策略记忆 ──

    def test_record_strategy(self):
        strategy = self.memory.record_strategy(
            task_type="goto",
            description="回家路径",
            action_sequence=[{"action": "walk_to", "x": 100}],
            success=True,
            duration=10.0,
        )
        assert strategy.success_count == 1
        assert strategy.success_rate == 1.0

    def test_best_strategy(self):
        self.memory.record_strategy("goto", "路径A", [{"a": 1}], success=True)
        self.memory.record_strategy("goto", "路径A", [{"a": 1}], success=True)
        self.memory.record_strategy("goto", "路径B", [{"b": 1}], success=False)
        best = self.memory.get_best_strategy("goto")
        assert best.description == "路径A"

    def test_strategy_with_context_tags(self):
        self.memory.record_strategy("mine", "白天挖矿", [{"a": 1}],
                                     success=True, context_tags=["daytime", "surface"])
        self.memory.record_strategy("mine", "夜间挖矿", [{"b": 1}],
                                     success=True, context_tags=["nighttime", "cave"])
        best = self.memory.get_best_strategy("mine", context_tags=["nighttime"])
        assert best.description == "夜间挖矿"

    # ── 玩家记忆 ──

    def test_player_memory(self):
        player = self.memory.get_or_create_player("Steve")
        assert player.player_name == "Steve"
        assert player.home_location is None

    def test_update_player_home(self):
        self.memory.update_player_home("Steve", (100, 64, 200))
        home = self.memory.get_player_home("Steve")
        assert home == (100, 64, 200)

    def test_record_interaction(self):
        self.memory.record_player_interaction("Steve")
        self.memory.record_player_interaction("Steve")
        player = self.memory.get_or_create_player("Steve")
        assert player.interaction_count == 2

    # ── 世界记忆 ──

    def test_spawn_point(self):
        self.memory.set_spawn_point((0, 64, 0))
        assert self.memory.world.spawn_point == (0, 64, 0)

    def test_safe_points(self):
        self.memory.add_safe_point((0, 64, 0))
        self.memory.add_safe_point((100, 64, 200))
        assert len(self.memory.world.safe_points) == 2

    def test_nearest_safe_point(self):
        self.memory.add_safe_point((0, 64, 0))
        self.memory.add_safe_point((100, 64, 200))
        nearest = self.memory.get_nearest_safe_point(90, 64, 190)
        assert nearest == (100, 64, 200)

    def test_record_event(self):
        self.memory.record_event("death", "被苦力怕炸死", (50, 64, 50))
        assert len(self.memory.world.notable_events) == 1

    # ── Baritone 集成 ──

    def test_exclusion_zones(self):
        self.memory.register_building("主城", (100, 64, 200), radius=20)
        self.memory.register_danger("岩浆湖", (80, 12, -50))
        exclusions = self.memory.get_exclusion_zones()
        assert len(exclusions) == 3  # building: no_break + no_place, danger: avoid

    def test_navigate_context(self):
        self.memory.register_building("主城", (100, 64, 200), radius=20)
        context = self.memory.get_navigate_context((0, 64, 0), (100, 64, 200))
        assert "exclusion_zones" in context
        assert "cached_path" in context
        assert len(context["nearby_protections"]) >= 1

    # ── AI 上下文 ──

    def test_ai_context_empty(self):
        ctx = self.memory.get_ai_context()
        assert "记忆系统" in ctx

    def test_ai_context_with_data(self):
        self.memory.register_base("家", (50, 64, -100))
        self.memory.register_danger("岩浆", (80, 12, -50))
        self.memory.cache_path((0, 64, 0), (50, 64, -100), [], success=True)
        self.memory.cache_path((0, 64, 0), (50, 64, -100), [], success=True)
        self.memory.cache_path((0, 64, 0), (50, 64, -100), [], success=True)
        ctx = self.memory.get_ai_context()
        assert "基地" in ctx
        assert "危险区域" in ctx

    # ── 持久化 ──

    def test_persistence(self):
        self.memory.register_building("主城", (100, 64, 200))
        self.memory.cache_path((0, 64, 0), (100, 64, 200), [(0, 64, 0)], success=True)
        self.memory.record_strategy("goto", "test", [{"a": 1}], success=True)
        self.memory.update_player_home("Steve", (100, 64, 200))
        self.memory.set_spawn_point((0, 64, 0))

        # 重新加载
        memory2 = GameMemory(storage_path=self.test_dir)
        assert "building_主城" in memory2.zones
        assert memory2.get_cached_path((0, 64, 0), (100, 64, 200)) is not None
        assert len(memory2.strategies) == 1
        assert memory2.get_player_home("Steve") == (100, 64, 200)
        assert memory2.world.spawn_point == (0, 64, 0)

    # ── 统计 ──

    def test_stats(self):
        self.memory.register_building("A", (100, 64, 200))
        self.memory.register_danger("B", (80, 12, -50))
        stats = self.memory.get_stats()
        assert stats["zones"] == 2
        assert stats["protected_zones"] == 1
