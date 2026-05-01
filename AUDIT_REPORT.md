# BlockMind 代码质量审计报告

**审计时间**: 2026-05-01  
**审计范围**: Python 后端 (70 files, ~3000 LOC) + Java Mod (8 files) + 配置/测试/CI/CD/文档

---

## 🔴 P0 — 严重安全漏洞（必须立即修复）

### 1. API Key 明文泄露在 config.yaml
- **文件**: `config.yaml:27-28`
- **问题**: 真实 API Key 已硬编码在本地 `config.yaml` 中（已被 `.gitignore` 排除，未提交到 git）。
- **修复**: 立即轮换 API Key，改用环境变量 (`BLOCKMIND_API_KEY`)，从 git history 中清除。

### 2. Java Mod HTTP API 完全无认证
- **文件**: `mod/src/main/java/blockmind/api/BlockMindHttpServer.java`
- **问题**: 端口 25580 的所有 API 端点（spawn bot、dig、attack、chat）均无任何认证。任何能访问该端口的人可以完全控制游戏。
- **修复**: 添加 API Key 或 HMAC 签名认证中间件。

### 3. CORS 配置完全开放
- **Python**: `src/webui/app.py:39` — `allow_origins=["*"]`
- **Java**: `BlockMindHttpServer.java:83` — `Access-Control-Allow-Origin: *`
- **问题**: 允许任意来源访问 API，存在 CSRF 风险。
- **修复**: 限制为实际使用的域名。

### 4. 密码哈希使用 SHA256（不安全）
- **文件**: `src/webui/auth.py:30`
- **问题**: `hashlib.sha256()` 无 salt，易被彩虹表攻击。
- **修复**: 改用 `bcrypt` 或 `argon2-cffi`。

### 5. WebSocket 端点无认证
- **文件**: `src/webui/app.py:80-88`
- **问题**: `/ws` WebSocket 端点不验证 token，任何人可连接获取实时游戏状态和日志。
- **修复**: 在 WebSocket 握手阶段验证 token。

---

## 🟠 P1 — 关键功能缺陷

### 6. app.py WebSocket 路由 Bug
- **文件**: `src/webui/app.py:82`
- **问题**: `engine.state.ws_manager` 应为 `app.state.ws_manager`，会导致运行时 AttributeError。
- **修复**: `await app.state.ws_manager.connect(ws)`

### 7. Java Mod ActionExecutor 多个动作未真正实现
- **`place()`**: 仅返回 success 但未实际放置方块
- **`eat()`**: 直接 `add(5, 0.5f)` 恢复饥饿值，不消耗物品
- **`PathfinderHandler.baritoneGoto()`**: Baritone 集成大部分为 stub，不实际导航
- **`basicGoto()`**: 仅返回 JSON 不执行移动
- **影响**: Python 后端调用这些 API 会得到虚假的"成功"响应。

### 8. EventListener 线程安全与多玩家问题
- **文件**: `mod/src/main/java/blockmind/event/EventListener.java:44-45`
- **问题**: `lastHealth`/`lastHunger` 是 static 字段，只追踪一个玩家状态。多玩家场景下会丢失事件。
- **修复**: 改用 `Map<UUID, PlayerState>` 追踪每个玩家。

### 9. StateCollector.getBlocks() 性能灾难
- **文件**: `mod/src/main/java/blockmind/collector/StateCollector.java:220-238`
- **问题**: 三层嵌套循环扫描方块，`radius=16` 时扫描 35,937 个方块，会导致严重卡顿。
- **修复**: 添加最大方块数量限制，使用增量扫描或缓存。

### 10. 13 个 TODO 标记的未完成实现
- `src/game/connection.py`: 9 个 TODO（pyCraft 连接、心跳、动作执行等全部未实现）
- `src/game/perception.py`: 4 个 TODO（玩家状态、方块解析等）
- `src/monitoring/fallback.py`: 1 个 TODO（安全点传送）

---

## 🟡 P2 — 代码质量问题

### 11. routes.py 过大（924 行）
- **建议**: 拆分为 `routes_auth.py`, `routes_skills.py`, `routes_marketplace.py`, `routes_memory.py`, `routes_config.py`, `routes_system.py`。

### 12. 过度使用宽泛异常捕获
- **数量**: ~30 处 `except Exception`，多处静默吞错。
- **典型问题**: `routes.py` 中远程注册中心调用全部 `except Exception: pass`，隐藏网络错误。
- **修复**: 捕获具体异常类型，记录日志。

### 13. `asyncio.get_event_loop()` 已弃用
- **位置**: 4 处（`main.py`, `websocket.py`, `task_classifier.py`, `authorizer.py`）
- **修复**: 改用 `asyncio.get_running_loop()` 或 `asyncio.get_event_loop()` → `asyncio.get_event_loop()` 在 3.10+ 已弃用。

### 14. Java Mod 手动 JSON 拼接
- **文件**: `BlockMindHttpServer.java:100-103` — `HealthHandler` 手动拼接 JSON 字符串。
- **修复**: 统一使用 Gson。

### 15. 路由中 `import time` 在函数内部
- **文件**: `routes.py:303` — `system_health` 函数内 `import time`。
- **修复**: 移到模块顶层。

### 16. config.example.yaml 与实际版本不一致
- `config.example.yaml:17` — `expected_version: "1.0.0"`
- `config.yaml:17` — `expected_version: "1.1.0"`
- **修复**: 同步版本号。

### 17. config.example.yaml 硬编码 IP 地址
- `config.example.yaml:28,34` — `base_url: 'http://38.246.244.201:8317/v1'`
- **修复**: 改为 `base_url: 'https://api.openai.com/v1'` 或留空使用默认值。

---

## 🔵 P3 — 测试与 CI/CD

### 18. 测试覆盖率极低
- **现状**: 3 个测试文件，仅覆盖 models、ModClient init、TaskClassifier、EventBus、ActionQueue、ChatHandler。
- **缺失**:
  - WebUI 路由测试（0%）
  - 认证/中间件测试（0%）
  - Skill 运行时测试（0%）
  - AI Provider 测试（0%）
  - 监控模块测试（0%）
  - Config loader 测试（0%）
  - Java Mod 测试（0%）
- **建议**: 优先为 WebUI routes 和 auth 添加测试，目标覆盖率 60%+。

### 19. CI 缺少 Lint 和安全扫描
- **缺失步骤**:
  - Python: ruff/flake8 lint, mypy 类型检查, bandit 安全扫描
  - Java: checkstyle, spotbugs
  - Docker: trivy 漏洞扫描
  - 代码覆盖率报告 (codecov)
- **建议**: 在 `build.yml` 中添加 lint job。

### 20. requirements.txt 无版本锁定
- **问题**: 仅指定最低版本 (`>=`)，不同时间安装可能得到不同版本。
- **修复**: 使用 `pip freeze > requirements.lock` 或 `pyproject.toml` + lock file。

---

## 🟢 P4 — 文档与工程规范

### 21. 缺少 API 文档
- Java Mod 有 20+ 个 HTTP 端点，但无 OpenAPI/Swagger 文档。
- Python WebUI 有 30+ 个路由，FastAPI 自动生成的 docs 未配置描述。
- **建议**: 为每个路由添加 `summary` 和 `description`。

### 22. 缺少 CONTRIBUTING.md 和 CHANGELOG.md
- 有 13 语言 README 但无贡献指南。
- **建议**: 添加 CHANGELOG.md 记录版本变更。

### 23. 缺少 `.env.example`
- 环境变量 `BLOCKMIND_PASSWORD`, `BLOCKMIND_CONFIG` 等未文档化。
- **建议**: 创建 `.env.example` 文件。

### 24. 缺少 `pyproject.toml`
- 项目使用非标准结构，无 `pyproject.toml` 或 `setup.py`。
- **建议**: 添加 `pyproject.toml` 规范化项目配置。

### 25. BotManager 线程安全
- **文件**: `mod/src/main/java/blockmind/bot/BotManager.java`
- **问题**: 所有字段为 static，HTTP 线程和游戏线程并发访问无同步。
- **修复**: 添加 `synchronized` 或使用 `AtomicReference`。

---

## 优化优先级总结

| 优先级 | 数量 | 关键行动 |
|--------|------|---------|
| 🔴 P0 | 5 | 轮换 API Key, 添加 Mod 认证, 修复 CORS, 升级密码哈希, WS 认证 |
| 🟠 P1 | 5 | 修复 app.py bug, 实现 Mod 动作, 线程安全, 性能优化, 完成 TODO |
| 🟡 P2 | 7 | 拆分 routes.py, 修复异常处理, 弃用 API, 配置同步 |
| 🔵 P3 | 3 | 扩展测试, CI lint/安全扫描, 版本锁定 |
| 🟢 P4 | 5 | API 文档, CONTRIBUTING.md, pyproject.toml, .env.example |

**总计**: 25 个优化项，其中 5 个安全漏洞需立即处理。
