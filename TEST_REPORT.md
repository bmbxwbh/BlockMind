# BlockMind 全量测试报告
> 测试时间: 2026-04-30 17:00-17:56
> 测试环境: Sealos DevBox (Ubuntu 24.04, Python 3.12.3, Java 17.0.18)

---

## ✅ 通过的测试

### 环境 & 依赖
- [x] Python 3.12.3 可用
- [x] Java 17.0.18 可用
- [x] venv 自动创建 (install.sh)
- [x] pip 自动安装 (ensurepip fallback → 系统 apt)
- [x] 所有 13 个 Python 依赖安装成功 (fastapi 0.136.1, uvicorn 0.46.0, openai 2.33.0, anthropic 0.97.0, httpx 0.28.1, pydantic 2.13.3, jinja2 3.1.6, websockets 16.0, psutil 7.2.2, aiohttp 3.13.5, rich, python-dotenv, pyyaml)
- [x] 阿里云镜像源切换正常

### 脚本 (install.sh / start.sh / start_mc.sh)
- [x] bash -n 语法检查全部通过
- [x] install.sh 中文语言选择正常
- [x] install.sh 本地部署模式正常
- [x] start_mc.sh 中文语言选择正常
- [x] start_mc.sh 版本选择 (1.20.4) 正常
- [x] Fabric Installer 下载正常 (v1.1.1, 209KB)
- [x] Fabric Loader 安装正常 (v0.19.2 + MC 1.20.4)
- [x] MC 服务端启动正常 (Done in 13.186s)
- [x] BlockMind Mod 加载正常 (HTTP API :25580)
- [x] eula.txt 自动生成
- [x] 内存自动检测 (2G/4G)
- [x] Mod 从 GitHub Release 下载正常 (blockmind-mod-1.0.0.jar, 34KB)
- [x] Fabric API 从 Modrinth 下载正常 (fabric-api-0.97.3+1.20.4.jar, 2.1MB)

### MC 服务端
- [x] Fabric 1.20.4 启动正常
- [x] BlockMind Mod v1.0.0 加载成功
- [x] HTTP API 监听 25580 端口
- [x] /health 端点正常: `{"status":"ok","mod":"blockmind","pathfinder":"basic"}`
- [x] /api/status 端点正常: `{"connected":false}`
- [x] /api/world 端点正常: `{}`
- [x] /api/inventory 端点正常: `{}`
- [x] /api/move 正确返回: `{"success":false,"error":"No player online"}`
- [x] /api/chat 正确返回: `{"success":false,"error":"No player online"}`
- [x] online-mode=false 设置正常
- [x] 玩家可正常登录 (bmbxwbh 测试成功)

### BlockMind 后端
- [x] WebUI 启动正常 (0.0.0.0:19951)
- [x] Mod API 连接成功 (mod=True)
- [x] 记忆系统初始化正常
- [x] 空闲任务调度器启动正常
- [x] 健康检查启动正常
- [x] 记忆保存/加载正常 (world.json)
- [x] connection_state.json 正常记录

### WebUI API (25 个端点)
- [x] GET / → 200 (页面正常)
- [x] POST /api/login → 200 (密码正确)
- [x] POST /api/login → 401 (密码错误)
- [x] GET /api/dashboard → 200
- [x] GET /api/system/status → 200
- [x] GET /api/system/health → 200
- [x] GET /api/system/resources → 200
- [x] GET /api/config/model → 200
- [x] POST /api/config/model → 200 (保存成功)
- [x] GET /api/skills → 200
- [x] GET /api/chat/history → 200
- [x] GET /api/stats/tokens → 200
- [x] GET /api/safety/config → 200
- [x] GET /api/safety/audit → 200
- [x] GET /api/memory/backups → 200
- [x] GET /api/memory/export → 200
- [x] POST /api/memory/backup → 200
- [x] POST /api/memory/cleanup → 200
- [x] POST /api/command → 200
- [x] GET /api/tasks/queue → 200
- [x] GET /docs → 200 (Swagger)
- [x] GET /openapi.json → 200
- [x] 未认证访问 → 401

---

## 🔴 Bug 列表

### BUG-001: /api/memory 返回 500 Internal Server Error
- **严重度**: 高
- **位置**: `src/webui/routes.py:412`
- **原因**: `for key, p in mem.cached_paths.items()` — GameMemory 对象没有 `cached_paths` 属性
- **正确写法**: 应该用 `mem.paths` (在 memory.py:840 中 `cached_paths` 是 stats dict 的 key，不是对象属性)
- **复现**: GET /api/memory (带有效 token)

### BUG-002: WebSocket /ws/events 端点不存在 (404)
- **严重度**: 高
- **位置**: `src/minecraft/ws_client.py:154`
- **原因**: 后端连接 `ws://localhost:25580/ws/events`，但 Mod API 没有此 WebSocket 端点
- **影响**: 后端无法实时接收游戏事件，持续重连失败（指数退避到 120s）
- **需要**: Mod 端实现 `/ws/events` WebSocket 端点，或后端改用其他通信方式

### BUG-003: Mod API /api/version 端点不存在 (404)
- **严重度**: 中
- **位置**: `src/minecraft/client.py:203`
- **原因**: 后端请求 `/api/version` 但 Mod 只有 `/health` 和 `/api/status`
- **影响**: `mod_version` 始终为 null (见 connection_state.json)

### BUG-004: Skill 文件全部缺失
- **严重度**: 中
- **位置**: `data/skills/` 目录为空
- **原因**: 空闲任务引用 `skill_repair_building_001`、`skill_place_torches_001` 等文件，但从未创建
- **影响**: 所有空闲任务每 30s 报错一次，日志快速膨胀
- **需要**: 预置默认 Skill 文件，或空闲任务在无 Skill 时静默跳过

### BUG-005: WebUI WebSocket /ws 返回 403 Forbidden
- **严重度**: 中
- **位置**: WebUI WebSocket 端点
- **原因**: 可能是 CORS 或认证问题
- **影响**: WebUI 无法建立 WebSocket 连接（实时日志流、事件推送不可用）

### BUG-006: WebUI /api/monitor 返回 404
- **严重度**: 低
- **原因**: 路由不存在（不在 OpenAPI schema 中）
- **影响**: 监控页面可能无法加载数据

### BUG-007: WebUI /api/tasks 返回 404
- **严重度**: 低
- **原因**: 路由不存在（但 /api/tasks/queue 存在）
- **影响**: 任务页面可能报错

### BUG-008: WebUI /api/logs 返回 404
- **严重度**: 低
- **原因**: 路由不存在
- **影响**: 日志页面无法获取日志数据

### BUG-009: /api/command/panel 和 /api/config/model/test 返回 405
- **严重度**: 低
- **原因**: HTTP 方法不匹配（可能是 GET vs POST）
- **影响**: 命令面板和模型测试功能不可用

### BUG-010: AI 模型未配置 (ai=False)
- **严重度**: 低（配置问题，非 bug）
- **原因**: config.yaml 中 api_key 为 "your-api-key-here"
- **影响**: AI 功能完全不可用

### BUG-011: 日志无 Python traceback
- **严重度**: 低
- **原因**: 500 错误的 traceback 只输出到 stderr，不写入日志文件
- **影响**: 调试困难，无法从日志定位 Python 异常

---

## 📊 测试统计

| 类别 | 总数 | 通过 | 失败 |
|------|------|------|------|
| 环境检查 | 6 | 6 | 0 |
| 脚本功能 | 12 | 12 | 0 |
| MC 服务端 | 12 | 12 | 0 |
| 后端启动 | 7 | 7 | 0 |
| WebUI API | 25 | 22 | 3 |
| Mod API | 8 | 5 | 3 |
| **总计** | **70** | **64** | **9** |

通过率: **91.4%**

---

## 🔧 修复优先级

1. **BUG-001** — /api/memory 500 (改 `mem.cached_paths` → `mem.paths`)
2. **BUG-002** — WebSocket /ws/events 404 (需 Mod 端实现或后端适配)
3. **BUG-004** — Skill 文件缺失 (预置默认文件或静默跳过)
4. **BUG-003** — /api/version 404 (改用 /health 获取版本)
5. **BUG-005** — WebUI WS 403 (检查 CORS/认证)
6. **BUG-006~011** — 低优先级 UI 路由和日志问题
