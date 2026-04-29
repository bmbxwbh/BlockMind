# 📋 BlockMind 开发任务清单 — v2.0（Fabric Mod 架构）

> 每个任务 = 一个 Claude Code 会话，包含精确文件路径、类签名、验收标准
> 项目根目录：`/root/projects/BlockMind/`

---

## 任务总览

| 阶段 | 名称 | 工期 | 任务数 | 状态 |
|------|------|------|--------|------|
| P0 | 项目初始化 | 0.5天 | 6 | ✅ 已完成 |
| P1 | Fabric Mod 开发 | 3天 | 8 | 🔲 待开始 |
| P2 | Mod 通信客户端 | 1天 | 4 | 🔲 待开始 |
| P3 | 游戏交互层 | 2天 | 7 | 🔲 待开始 |
| P4 | Skill DSL 引擎 | 4天 | 12 | 🔲 待开始 |
| P5 | AI 决策模块 | 3天 | 5 | 🔲 待开始 |
| P6 | 安全校验层 | 2天 | 8 | 🔲 待开始 |
| P7 | 故障监控 | 2天 | 7 | 🔲 待开始 |
| P8 | 空闲任务 | 1天 | 5 | 🔲 待开始 |
| P9 | WebUI | 3天 | 10 | 🔲 待开始 |
| P10 | 部署运维 | 1.5天 | 6 | 🔲 待开始 |
| P11 | 测试优化 | 2天 | 7 | 🔲 待开始 |
| **合计** | | **~25天** | **85** | |

---

## P0: 项目初始化 ✅ 已完成

| # | 任务 | 状态 |
|---|------|------|
| 0.1 | 目录结构 + __init__.py | ✅ |
| 0.2 | Git 初始化 + .gitignore | ✅ |
| 0.3 | requirements.txt | ✅ |
| 0.4 | config.example.yaml | ✅ |
| 0.5 | src/utils/logger.py | ✅ |
| 0.6 | src/core/event_bus.py + engine.py | ✅ |

---

## P1: Fabric Mod 开发（3 天）⭐ 新增

### Task 1.1 — Mod 项目初始化

```
目标：创建 Fabric Mod 项目骨架
工作目录：/root/projects/BlockMind/mod/
```

**需要创建的文件：**
- `build.gradle` — Gradle 构建配置（Fabric Loom）
- `src/main/resources/fabric.mod.json` — Mod 元数据
- `src/main/java/blockmind/BlockMindMod.java` — Mod 入口类

**build.gradle 关键配置：**
```groovy
plugins {
    id 'fabric-loom' version '1.6-SNAPSHOT'
}
dependencies {
    minecraft "com.mojang:minecraft:1.20.4"
    mappings "net.fabricmc:yarn:1.20.4+build.3:v2"
    modImplementation "net.fabricmc.fabric-api:fabric-api:0.92.0+1.20.4"
    implementation "com.sun.net.httpserver:http:20230601"  // 内置 HTTP 服务器
}
```

**BlockMindMod.java：**
```java
public class BlockMindMod implements ModInitializer {
    public static final String MOD_ID = "blockmind";
    private static HttpServer httpServer;

    @Override
    public void onInitialize() {
        // 启动 HTTP API 服务
        httpServer = new BlockMindHttpServer(25580);
        httpServer.start();
        // 注册事件监听
        new EventListener().register();
    }
}
```

**验收：** `./gradlew build` 成功产出 jar

---

### Task 1.2 — HTTP API 服务

```
目标：实现 HTTP API 服务端
工作目录：/root/projects/BlockMind/mod/
```

**需要创建的文件：**
- `src/main/java/blockmind/api/HttpServer.java` — HTTP 服务器
- `src/main/java/blockmind/api/Routes.java` — 路由定义
- `src/main/java/blockmind/api/JsonUtil.java` — JSON 工具

**API 端点：**
```
GET  /api/status        — 机器人状态
GET  /api/world         — 世界状态
GET  /api/inventory     — 背包
GET  /api/entities      — 附近实体
GET  /api/blocks        — 附近方块
POST /api/move          — 移动
POST /api/dig           — 挖掘
POST /api/place         — 放置
POST /api/attack        — 攻击
POST /api/eat           — 进食
POST /api/look          — 看向位置
POST /api/chat          — 发送聊天
GET  /health            — 健康检查
```

**验收：** 服务器启动后 `curl http://localhost:25580/health` 返回 200

---

### Task 1.3 — 状态采集器（Java）

```
目标：实现游戏状态采集
工作目录：/root/projects/BlockMind/mod/
```

**需要创建的文件：**
- `src/main/java/blockmind/collector/StateCollector.java`
- `src/main/java/blockmind/collector/EntityCollector.java`
- `src/main/java/blockmind/collector/BlockCollector.java`

**核心方法：**
```java
public class StateCollector {
    public static JsonObject getStatus()      // 玩家状态
    public static JsonObject getWorld()       // 世界状态
    public static JsonObject getInventory()   // 背包
    public static JsonObject getEntities(int radius)  // 实体
    public static JsonObject getBlocks(int radius, String type)  // 方块
}
```

**验收：** 在游戏中执行 `/api/status` 返回正确的血量、位置

---

### Task 1.4 — 动作执行器（Java）

```
目标：实现游戏动作执行
工作目录：/root/projects/BlockMind/mod/
```

**需要创建的文件：**
- `src/main/java/blockmind/executor/ActionExecutor.java`
- `src/main/java/blockmind/executor/MoveExecutor.java`
- `src/main/java/blockmind/executor/DigExecutor.java`

**核心方法：**
```java
public class ActionExecutor {
    public static JsonObject move(double x, double y, double z, boolean sprint)
    public static JsonObject dig(int x, int y, int z)
    public static JsonObject place(String item, int x, int y, int z)
    public static JsonObject attack(int entityId)
    public static JsonObject eat(String item)
    public static JsonObject look(double x, double y, double z)
    public static JsonObject chat(String message)
}
```

**验收：** POST /api/move 机器人实际移动

---

### Task 1.5 — 事件监听器（Java）

```
目标：监听游戏事件并推送到 WebSocket
工作目录：/root/projects/BlockMind/mod/
```

**需要创建的文件：**
- `src/main/java/blockmind/event/EventListener.java`
- `src/main/java/blockmind/event/ChatListener.java`
- `src/main/java/blockmind/api/WebSocketHandler.java`

**监听的事件：**
```java
// 聊天消息
ServerMessageEvents.CHAT_MESSAGE
// 玩家伤害
ServerLivingEntityEvents.AFTER_DAMAGE
// 方块变化
ServerBlockWorldEvents.AFTER_PLACE / AFTER_BREAK
// 实体生成/消失
ServerEntityEvents.ENTITY_LOAD / UNLOAD
// 玩家死亡
ServerLivingEntityEvents.ALLOW_DEATH
```

**WebSocket 推送格式：**
```json
{"type": "chat", "data": {"player": "Steve", "message": "hi"}}
{"type": "damage", "data": {"source": "zombie", "amount": 3.0}}
{"type": "block_change", "data": {"pos": [1,2,3], "old": "air", "new": "stone"}}
```

**验收：** 在游戏聊天发消息，WebSocket 收到事件

---

### Task 1.6 — Mod 配置文件

```
目标：支持 Mod 端配置
工作目录：/root/projects/BlockMind/mod/
```

**需要创建的文件：**
- `src/main/java/blockmind/config/ModConfig.java`

**配置项：**
```json
{
  "http_port": 25580,
  "ws_enabled": true,
  "log_level": "INFO",
  "allowed_ips": ["127.0.0.1"],
  "max_scan_radius": 64
}
```

---

### Task 1.7 — Mod 测试

```
目标：Mod 功能测试
工作目录：/root/projects/BlockMind/mod/
```

**测试清单：**
- [ ] Mod 可正常加载
- [ ] HTTP API 所有端点正常
- [ ] WebSocket 事件推送正常
- [ ] 动作执行后游戏状态变化
- [ ] 多客户端并发访问

---

### Task 1.8 — Mod 文档

```
目标：编写 Mod README
工作目录：/root/projects/BlockMind/mod/README.md
```

---

## P2: Mod 通信客户端（1 天）

### Task 2.1 — HTTP 客户端

```
目标：Python 端 Mod HTTP 客户端
工作目录：/root/projects/BlockMind/
```

**需要创建的文件：** `src/mod_client/client.py`

```python
class ModClient:
    """Fabric Mod HTTP 客户端"""

    def __init__(self, host: str, port: int):
        self.base_url = f"http://{host}:{port}"
        self._session: Optional[aiohttp.ClientSession] = None

    async def connect(self) -> bool
    async def disconnect(self) -> None
    async def health_check(self) -> bool

    # 状态查询
    async def get_status(self) -> dict
    async def get_world(self) -> dict
    async def get_inventory(self) -> dict
    async def get_entities(self, radius: int = 32) -> dict
    async def get_blocks(self, radius: int = 32, block_type: str = None) -> dict

    # 动作执行
    async def move(self, x, y, z, sprint=False) -> dict
    async def dig(self, x, y, z) -> dict
    async def place(self, item, x, y, z) -> dict
    async def attack(self, entity_id) -> dict
    async def eat(self, item) -> dict
    async def look(self, x, y, z) -> dict
    async def chat(self, message) -> dict
```

**验收：** `ModClient` 可实例化，所有方法签名正确

---

### Task 2.2 — WebSocket 客户端

```
目标：接收 Mod 推送的实时事件
工作目录：/root/projects/BlockMind/
```

**需要创建的文件：** `src/mod_client/ws_client.py`

```python
class ModWebSocketClient:
    """Mod WebSocket 客户端"""

    def __init__(self, host: str, port: int, event_bus: EventBus):
        self.url = f"ws://{host}:{port}/ws/events"

    async def connect(self) -> None
    async def disconnect(self) -> None
    async def _listen(self) -> None  # 持续监听并 emit 到 EventBus
```

---

### Task 2.3 — 数据模型

```
目标：定义 Mod API 的数据模型
工作目录：/root/projects/BlockMind/
```

**需要创建的文件：** `src/mod_client/models.py`

```python
class PlayerStatus(BaseModel): ...
class WorldState(BaseModel): ...
class InventoryItem(BaseModel): ...
class EntityInfo(BaseModel): ...
class BlockInfo(BaseModel): ...
class ActionResult(BaseModel): ...
```

---

### Task 2.4 — 客户端测试

**需要创建的文件：** `tests/test_mod_client.py`

---

## P3: 游戏交互层（2 天）

### Task 3.1 — 状态感知器

**文件：** `src/game/perception.py`
**输入：** ModClient

### Task 3.2 — 背包管理器

**文件：** `src/game/inventory.py`

### Task 3.3 — 动作执行器

**文件：** `src/game/actions.py`

### Task 3.4 — 动作队列

**文件：** `src/game/action_queue.py`

### Task 3.5 — 聊天交互

**文件：** `src/game/chat.py`

### Task 3.6 — 寻路算法

**文件：** `src/game/pathfinding.py`

### Task 3.7 — 游戏层测试

**文件：** `tests/test_game.py`

---

## P4-P11: 后续模块

> P4（Skill DSL）、P5（AI 决策）、P6（安全校验）、P7（故障监控）、
> P8（空闲任务）、P9（WebUI）、P10（部署）、P11（测试）
> 与原版相同，待后续展开。

---

## 📊 依赖关系

```
P0 → P1 (Mod) → P2 (客户端) → P3 (游戏层)
                                    ↓
                              P4 (Skill) → P5 (AI)
                                    ↓
                              P6 (安全) → P7 (监控) → P8 (空闲)
                                    ↓
                              P9 (WebUI) → P10 (部署) → P11 (测试)
```

---

<p align="center">
  <i>📋 BlockMind 任务清单 v2.0 · Fabric Mod 架构 · 星糯 🎀</i>
</p>
