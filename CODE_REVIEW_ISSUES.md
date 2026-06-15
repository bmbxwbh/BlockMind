# BlockMind 代码审查问题清单

> 审查日期：2026-06-14
> 修复日期：2026-06-14
> 审查范围：Python 后端、Fabric Mod (Java)、Skills/Config/Scripts/Tests/GitHub Actions

---

## 修复状态汇总

| 严重度 | 总数 | 已修复 | 剩余 |
|--------|------|--------|------|
| 致命/崩溃 | 11 | **11** | 0 |
| 安全 | 9 | **8** | 1 (S6标记TODO) |
| 功能缺陷 | 7 | **7** | 0 |
| 内存泄漏 | 6 | **6** | 0 |
| 性能 | 5 | **4** | 1 (P4未修) |
| 线程安全 | 4 | **4** | 0 |
| 部署/脚本 | 8 | **8** | 0 |
| 数据不一致 | 5 | **4** | 1 (X5文档) |
| CI/CD/测试 | 6 | 0 | 6 (需独立规划) |
| **合计** | **61** | **52** | **9** |

---

## 一、致命/崩溃级问题（11/11 ✅）

| # | 状态 | 问题描述 | 文件位置 | 修复方式 |
|---|------|----------|----------|----------|
| 1 | ✅ | `asyncio.gather` 传入 `None`，WebUI关闭时启动崩溃 | `src/main.py:58` | 条件添加 webui_task |
| 2 | ✅ | `MainAgent.chat()` 不接受 `context` 参数 | `src/ai/main_agent.py:52` | 添加 `context: str = ""` 参数 |
| 3 | ✅ | `OperationAgent.execute()` 不接受 `context` 参数 | `src/ai/operation_agent.py:41` | 添加 `context: str = ""` 参数 |
| 4 | ✅ | EventBus 通配符 `"*"` 不生效 | `src/core/event_bus.py:64` | emit() 中合并 wildcard handlers |
| 5 | ✅ | A*寻路每个方块发HTTP请求（性能灾难） | `src/game/pathfinding.py:132` | `_is_passable` 改为接收 block_type 参数 |
| 6 | ✅ | `_execute_cached_path` 返回 bool 访问 .success 崩溃 | `src/game/navigation.py:358` | 返回 NavigationResult 对象 |
| 7 | ✅ | `run_until_complete()` 在运行中的事件循环调用 | `src/core/task_classifier.py:140` | 改为 async/await |
| 8 | ✅ | MC API 在 HTTP 线程调用（JVM崩溃） | `ActionExecutor/StateCollector.java` | 通过 server.execute() 调度到 Tick 线程 |
| 9 | ✅ | Baritone 集成完全不工作 | `PathfinderHandler.java` | 取消注释 setGoalAndPath，实现 basicGoto |
| 10 | ✅ | `place()` 是空壳 | `ActionExecutor.java:129` | 实现 Registry 方块查找 + setBlockState |
| 11 | ✅ | EventListener listeners 非线程安全 | `EventListener.java:23` | 改为 CopyOnWriteArrayList |

---

## 二、安全问题（8/9 ✅）

| # | 状态 | 问题描述 | 文件位置 | 修复方式 |
|---|------|----------|----------|----------|
| S1 | ✅ | API Key 明文写入 config.yaml | `src/webui/routes.py:547` | 写入前脱敏为 `"***"` |
| S2 | ✅ | WebUI 默认密码 `blockmind` | `src/webui/auth.py:21` | 默认改为空字符串，启动时警告 |
| S3 | ✅ | `/api/entities` 和 `/api/blocks` 无鉴权 | `BlockMindHttpServer.java:148` | 添加 checkAuth() 调用 |
| S4 | ✅ | HTTP 请求无 body 大小限制 | `BlockMindHttpServer.java:107` | 限制 64KB |
| S5 | ✅ | config.example.yaml 硬编码外部 IP | `config.example.yaml:27,34` | 替换为 `https://api.openai.com/v1` |
| S6 | 🔶 | CORS/IP白名单配置未实现 | `src/config/loader.py:200` | 标记为 TODO（避免误导） |
| S7 | ✅ | API Token 时序攻击 | `BlockMindHttpServer.java:92` | 改用 MessageDigest.isEqual() |
| S8 | ✅ | `dig()` 跳过游戏机制 | `ActionExecutor.java:111` | 使用 world.breakBlock() 模拟真实挖掘 |
| S9 | ✅ | DSL `_safe_eval` 属性无白名单 | `src/skills/control_flow.py:122` | 添加属性白名单检查 |

---

## 三、功能缺陷（7/7 ✅）

| # | 状态 | 问题描述 | 文件位置 | 修复方式 |
|---|------|----------|----------|----------|
| F1 | ✅ | EmergencyTakeover 只识别 walk_to/eat | `src/ai/takeover.py:32` | 添加 move/attack/place/look/dig/chat |
| F2 | ✅ | TaskPool 硬编码 skill_id 不存在 | `src/core/task_pool.py:22` | 改为匹配实际文件名 |
| F3 | ✅ | eat() 硬编码食物值 | `ActionExecutor.java:195` | 添加 35 种食物查找表 |
| F4 | ✅ | kill_ender_dragon 用末影珍珠进末地 | `skills/marketplace/kill_ender_dragon.yaml:33` | 修改为眼睛传送门流程 |
| F5 | ✅ | Bot 未注册到 Minecraft Server | `BotManager.java:49` | 调用 PlayerManager.onPlayerConnect() |
| F6 | ✅ | `_is_solid` 子串匹配误判 | `src/game/pathfinding.py:157` | 改为精确集合匹配 |
| F7 | ✅ | Marketplace 导出丢失 when.any | `src/skills/marketplace.py:453` | 导出时包含 when.any |

---

## 四、内存泄漏（6/6 ✅）

| # | 状态 | 问题描述 | 文件位置 | 修复方式 |
|---|------|----------|----------|----------|
| M1 | ✅ | `_block_cache` 无上限 | `src/game/pathfinding.py:50` | OrderedDict LRU 淘汰 (max 10000) |
| M2 | ✅ | `_alert_history` 无清理 | `src/monitoring/alerter.py:42` | 限制 1000 条 |
| M3 | ✅ | `_rate_store` 无清理 | `src/webui/middleware.py:23` | 定期清理 1 小时前的条目 |
| M4 | ✅ | `_sessions` 无清理 | `src/webui/auth.py:27` | verify_session() 中调用 cleanup_expired() |
| M5 | ✅ | playerStates 玩家断开不移除 | `EventListener.java:25` | Tick 中检测并移除断开玩家 |
| M6 | ✅ | HTTP 线程池不 shutdown | `BlockMindHttpServer.java:42` | stop() 中调用 executorService.shutdown() |

---

## 五、性能问题（4/5 ✅）

| # | 状态 | 问题描述 | 文件位置 | 修复方式 |
|---|------|----------|----------|----------|
| P1 | ✅ | list_all() 每次解析所有 YAML | `src/skills/storage.py:56` | 添加 _list_cache 缓存 |
| P2 | ✅ | get() rglob 全目录 | `src/skills/storage.py:40` | 复用 list_all() 缓存 |
| P3 | ✅ | _detect_cluster_zones O(N³) | `src/game/navigation.py:386` | 预构建邻接表降为 O(N²) |
| P4 | ❌ | urllib.request 阻塞事件循环 | `marketplace.py:181`, `registry.py:231` | 未修（需改为 httpx/aiohttp） |
| P5 | ✅ | CircuitBreaker.trip() 阻塞 60s | `src/monitoring/circuit_breaker.py:23` | 改用 asyncio.create_task |

---

## 六、线程安全（4/4 ✅）

| # | 状态 | 问题描述 | 文件位置 | 修复方式 |
|---|------|----------|----------|----------|
| T1 | ✅ | ActionQueue 并发检查在锁外 | `src/game/action_queue.py:100` | 容量检查移入锁内 |
| T2 | ✅ | BotManager 复合操作非原子 | `ActionExecutor/StateCollector.java` | synchronized on BotManager.class |
| T3 | ✅ | VersionCompat.getCompat() 竞态 | `VersionCompat.java:125` | 添加 synchronized |
| T4 | ✅ | staticApiToken 竞态 | `BlockMindHttpServer.java:40` | 改为 volatile |

---

## 七、部署/脚本（8/8 ✅）

| # | 状态 | 问题描述 | 文件位置 | 修复方式 |
|---|------|----------|----------|----------|
| D1 | ✅ | check_completeness.py 硬编码路径 | `scripts/check_completeness.py:5` | 动态获取项目根目录 |
| D2 | ✅ | start_mc.bat T_USE_EXISTING 未定义 | `start_mc.bat:173` | 添加变量定义 |
| D3 | ✅ | start_mc.bat URL 解析脆弱 | `start_mc.bat:257` | 改进解析逻辑 |
| D4 | ✅ | start_mc.sh 硬编码版本 1.2.0 | `start_mc.sh:296` | 去除硬编码版本 |
| D5 | ✅ | start_all.bat 嵌套引号错误 | `start_all.bat:62` | 修正引号转义 |
| D6 | ✅ | healthcheck.sh pgrep 匹配自身 | `scripts/healthcheck.sh:42` | 改用更精确的匹配模式 |
| D7 | ✅ | docker-compose 内存限制过低 | `docker-compose.yaml:29` | 从 512M 增至 1024M |
| D8 | ✅ | pyCraft 依赖不一致 | `pyproject.toml` | 添加 pyCraft>=0.1.0 |

---

## 八、数据不一致（4/5 ✅）

| # | 状态 | 问题描述 | 文件位置 | 修复方式 |
|---|------|----------|----------|----------|
| X1 | ✅ | .index.json 版本号不匹配 | `skills/marketplace/.index.json` | 从 YAML 重新生成 |
| X2 | ✅ | .index.json 路径指向不存在子目录 | `skills/marketplace/.index.json` | 改为扁平路径 |
| X3 | ✅ | .index.json 评分/下载量不一致 | `skills/marketplace/.index.json` | 从 YAML 同步数据 |
| X4 | ✅ | Mod 日志版本 v1.1.0 vs 1.2.0 | `BlockMindMod.java:35` | 改为 v1.2.0 |
| X5 | ❌ | 文档硬编码路径 | `docs/TASKS.md` | 未修（文档类，低优先） |

---

## 九、CI/CD/测试（0/6 ❌ 未修）

> 以下问题需要独立规划，涉及 CI 工作流重构和大量测试编写，不在本次修复范围内。

| # | 状态 | 问题描述 |
|---|------|----------|
| C1 | ❌ | 全项目仅2个测试文件，多模块零测试 |
| C2 | ❌ | 无集成测试 |
| C3 | ❌ | CI无代码lint检查 |
| C4 | ❌ | CI无安全扫描 |
| C5 | ❌ | skills.yml 验证不充分 |
| C6 | ❌ | skills.yml 只在main触发，PR不触发 |
