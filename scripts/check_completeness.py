#!/usr/bin/env python3
"""BlockMind 项目完整性检查"""
import os, sys, py_compile, json

sys.path.insert(0, "/root/projects/BlockMind")
os.chdir("/root/projects/BlockMind")

report = {"errors": [], "warnings": [], "missing": [], "stats": {}}

# 1. 语法检查
syntax_errors = []
for dp, dn, fn in os.walk("src"):
    for f in fn:
        if f.endswith(".py"):
            path = os.path.join(dp, f)
            try:
                py_compile.compile(path, doraise=True)
            except py_compile.PyCompileError as e:
                syntax_errors.append(str(e))
report["syntax_errors"] = syntax_errors

# 2. 检查 engine.py 引用的模块是否存在
engine_imports = [
    "src/config/loader.py", "src/core/event_bus.py",
    "src/mod_client/client.py", "src/mod_client/ws_client.py",
    "src/game/perception.py", "src/game/actions.py", "src/game/action_queue.py",
    "src/game/inventory.py", "src/game/chat.py", "src/game/pathfinding.py",
    "src/skills/runtime.py", "src/skills/storage.py", "src/skills/matcher.py",
    "src/ai/provider.py", "src/ai/generator.py", "src/ai/takeover.py",
    "src/safety/gateway.py",
    "src/monitoring/health.py", "src/monitoring/fallback.py",
    "src/monitoring/alerter.py", "src/monitoring/circuit_breaker.py",
    "src/core/task_classifier.py", "src/core/task_router.py",
    "src/core/idle_detector.py", "src/core/task_pool.py", "src/core/idle_scheduler.py",
]
missing_files = [f for f in engine_imports if not os.path.exists(f)]
report["missing_engine_deps"] = missing_files

# 3. 检查 __init__.py
init_dirs = []
for dp, dn, fn in os.walk("src"):
    if any(f.endswith(".py") for f in fn) and "__init__.py" not in fn:
        init_dirs.append(dp)
report["missing_init"] = init_dirs

# 4. 检查 Skill YAML 文件
skill_files = []
for dp, dn, fn in os.walk("skills"):
    for f in fn:
        if f.endswith(".yaml") or f.endswith(".yml"):
            skill_files.append(os.path.join(dp, f))
report["skill_yamls"] = skill_files
report["skill_yaml_count"] = len(skill_files)

# 5. 检查 tasks 里引用的 skill 路径
task_registry_refs = [
    "skills/builtin/survival/eat_food.yaml",
    "skills/builtin/storage/deposit_items.yaml",
    "skills/builtin/storage/organize_chest.yaml",
    "skills/builtin/survival/sleep.yaml",
    "skills/builtin/navigation/go_home.yaml",
    "skills/builtin/gathering/chop_tree.yaml",
    "skills/builtin/gathering/mine_ore.yaml",
    "skills/builtin/farming/plant_wheat.yaml",
    "skills/builtin/gathering/collect.yaml",
    "skills/builtin/gathering/fish.yaml",
    "skills/builtin/combat/kill_mob.yaml",
]
missing_skills = [s for s in task_registry_refs if not os.path.exists(s)]
report["missing_skills"] = missing_skills

# 6. 统计
py_count = sum(1 for dp, dn, fn in os.walk("src") for f in fn if f.endswith(".py"))
java_count = sum(1 for dp, dn, fn in os.walk("mod") for f in fn if f.endswith(".java"))
total_lines = 0
for dp, dn, fn in os.walk("."):
    if ".git" in dp or "venv" in dp or "__pycache__" in dp:
        continue
    for f in fn:
        if f.endswith(".py") or f.endswith(".java"):
            try:
                with open(os.path.join(dp, f)) as fh:
                    total_lines += sum(1 for _ in fh)
            except:
                pass
report["stats"] = {"python_files": py_count, "java_files": java_count, "total_code_lines": total_lines}

# 7. 检查 config.example.yaml 是否存在
report["config_exists"] = os.path.exists("config/config.example.yaml")
report["dockerfile_exists"] = os.path.exists("Dockerfile")
report["docker_compose_exists"] = os.path.exists("docker-compose.yaml")
report["requirements_exists"] = os.path.exists("requirements.txt")
report["systemd_exists"] = os.path.exists("scripts/blockmind.service")

# 8. 检查 WebUI 前端
report["webui_template_exists"] = os.path.exists("src/webui/templates/index.html")

# 9. 检查 tests
report["test_files"] = [f for f in os.listdir("tests") if f.endswith(".py")]

print(json.dumps(report, indent=2, ensure_ascii=False))
