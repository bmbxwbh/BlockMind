# 🧠 BlockMind — 智能 Minecraft AI 玩伴系统

> **Fabric Mod + AI 驱动** · v2.0 · 2026-04-29

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![Fabric](https://img.shields.io/badge/Fabric-0.92+-yellow.svg)](https://fabricmc.net)
[![MC](https://img.shields.io/badge/Minecraft-1.20.x--1.21.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**一句话概括：** Fabric Mod 提供精准游戏接口 + Python 后端驱动 AI 决策，实现 7×24 小时自主生存的 Minecraft 智能玩伴。

---

## 📖 目录

- [项目特色](#-项目特色)
- [系统架构](#-系统架构)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [Fabric Mod API](#-fabric-mod-api)
- [核心模块](#-核心模块)
- [任务分类系统](#-任务分类系统)
- [Skill DSL 系统](#-skill-dsl-系统)
- [安全体系](#-安全体系)
- [故障容错](#-故障容错)
- [空闲自主任务](#-空闲自主任务系统)
- [WebUI 控制面板](#-webui-控制面板)
- [配置参考](#-配置参考)
- [部署指南](#-部署指南)
- [开发指南](#-开发指南)
- [故障排查](#-故障排查)
- [FAQ](#-faq)
- [路线图](#-路线图)
- [更新日志](#-更新日志)

---

## ✨ 项目特色

### 🧠 Skill DSL 固化复用 — 核心创新

```
传统方式：  玩家指令 → AI 思考 → 执行 → 下次再思考（每次消耗 Token）
Skill 方式：玩家指令 → AI 思考 → 生成 Skill → 执行 → 永久复用（零 Token）
```

AI 决策一次，生成 DSL Skill 文件，之后 **零 token 反复执行**。就像给机器人学会了"肌肉记忆"。

### 🔌 Fabric Mod 架构 — 精准可靠

```
传统方式：  Python Bot 解析 MC 协议 → 数据不准、动作不稳
Mod 方式：  Fabric Mod 直接调用游戏 API → 精准状态、可靠动作
```

不再依赖过时的 pyCraft，直接用 Fabric Mod 访问游戏内部 API，**零协议解析、零数据丢失**。

### 🛡️ 五级安全体系

| 等级 | 名称 | 示例 | 策略 |
|------|------|------|------|
| 0 | 完全安全 | 移动、跳跃 | 自动执行 |
| 1 | 低风险 | 挖泥土、放火把 | 自动执行 |
| 2 | 中风险 | 挖矿石、攻击中立生物 | 自动执行 |
| 3 | 高风险 | 点燃TNT、放岩浆 | 需玩家授权 |
| 4 | 致命风险 | 放命令方块 | 默认禁止 |

### 🔧 其他亮点

- **7×24 云服务器常驻**：Systemd 托管，断线自动重连
- **空闲自主行动**：没人指令时自动种田、挖矿、整理仓库
- **故障三级降级**：自动重试 → 终止回安全点 → AI 紧急接管
- **远程玩家干预**：聊天框发指令即可控制机器人
- **WebUI 控制面板**：可视化管理 Skill、监控状态、配置安全规则

---

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Minecraft 服务器                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              BlockMind Fabric Mod (Java)               │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐    │  │
│  │  │  状态采集器   │ │  动作执行器  │ │  事件监听器   │    │  │
│  │  │  方块/实体/  │ │  移动/挖掘/ │ │  聊天/伤害/  │    │  │
│  │  │  背包/世界   │ │  放置/攻击  │ │  方块变化    │    │  │
│  │  └──────┬──────┘ └──────┬──────┘ └──────┬───────┘    │  │
│  │         └───────────────┼───────────────┘             │  │
│  │                   HTTP API :25580                      │  │
│  │                   WebSocket /ws/events                 │  │
│  └───────────────────────────┼───────────────────────────┘  │
└──────────────────────────────┼──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  BlockMind Python 后端                       │
│                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐   │
│  │  Mod 客户端   │ │  状态管理器   │ │  动作队列        │   │
│  │  HTTP/WS 通信 │ │  快照对比    │ │  超时/取消/重试  │   │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────────┘   │
│         └────────────────┼────────────────┘                │
│  ┌───────────────────────┼────────────────────────────┐    │
│  │                  事件总线 (EventBus)                │    │
│  └───┬───────────┬───────┼───────┬───────────┬────────┘    │
│      │           │       │       │           │              │
│  ┌───▼───┐ ┌────▼──┐ ┌──▼──┐ ┌──▼───┐ ┌────▼────┐        │
│  │Skill  │ │ AI    │ │安全 │ │故障  │ │空闲任务 │        │
│  │引擎   │ │决策层 │ │校验 │ │监控  │ │调度器   │        │
│  └───────┘ └───────┘ └─────┘ └──────┘ └─────────┘        │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │              WebUI 控制面板 (FastAPI)               │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 数据流示例

**正常任务执行：**
```
玩家指令 "!砍树"
    → ChatHandler 解析指令
    → SkillMatcher 匹配 Skill
    → SkillRuntime 执行 DSL
    → ActionExecutor 调用 Mod API
    → Fabric Mod 执行游戏动作
    → StateCollector 采集结果
    → 返回执行状态
```

**新任务处理：**
```
玩家指令 "!建个房子"
    → SkillMatcher 未找到匹配
    → AIDecider 生成 Skill DSL
    → SkillValidator 校验
    → 存入 SkillStorage
    → SkillRuntime 执行
```

**故障处理：**
```
执行中检测到血量过低
    → ErrorClassifier 评级 3 级
    → CircuitBreaker 熔断
    → EmergencyTakeover AI 接管
    → AI 直接控制机器人回安全点
    → AutoReparer 修复出错 Skill
```

---

## 🚀 快速开始

### 环境要求

| 组件 | 要求 |
|------|------|
| **操作系统** | Ubuntu 22.04 LTS（推荐） |
| **Python** | 3.9+ |
| **Java** | 17+（编译 Mod） |
| **Minecraft** | 1.20.x - 1.21.x |
| **服务器** | Fabric Loader 0.92+ |
| **内存** | ≥ 4GB（服务器 + Python） |
| **磁盘** | ≥ 20GB |

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

# 2. 安装 Python 依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 编译 Fabric Mod（需要 Java 17+）
cd mod
./gradlew build
# 产出：mod/build/libs/blockmind-mod-1.0.0.jar

# 4. 安装 Mod 到服务器
cp build/libs/blockmind-mod-1.0.0.jar /path/to/server/mods/

# 5. 配置 Python 后端
cd ..
cp config.example.yaml config.yaml
# 编辑 config.yaml

# 6. 启动
python -m src.main
```

### 最小配置

```yaml
# config.yaml
mod:
  host: "localhost"
  port: 25580

game:
  server_ip: "localhost"
  server_port: 25565
  username: "BlockMind"

ai:
  provider: "openai"
  api_key: "your-api-key"
  model: "gpt-4o"

webui:
  enabled: true
  port: 8080
  password: "your-password"
```

---

## 📁 项目结构

```
BlockMind/
├── mod/                          # Fabric Mod (Java)
│   ├── src/main/java/blockmind/
│   │   ├── BlockMindMod.java     # Mod 入口
│   │   ├── api/
│   │   │   ├── HttpServer.java   # HTTP API 服务
│   │   │   ├── WebSocketHandler.java
│   │   │   └── Routes.java       # 路由定义
│   │   ├── collector/
│   │   │   ├── StateCollector.java    # 状态采集
│   │   │   ├── EntityCollector.java   # 实体采集
│   │   │   └── BlockCollector.java    # 方块采集
│   │   ├── executor/
│   │   │   ├── ActionExecutor.java    # 动作执行
│   │   │   ├── MoveExecutor.java      # 移动
│   │   │   └── DigExecutor.java       # 挖掘
│   │   └── event/
│   │       ├── EventListener.java     # 事件监听
│   │       └── ChatListener.java      # 聊天监听
│   ├── src/main/resources/
│   │   └── fabric.mod.json
│   ├── build.gradle
│   └── README.md
│
├── src/                          # Python 后端
│   ├── main.py                   # 主入口
│   ├── core/
│   │   ├── engine.py             # 核心引擎
│   │   ├── event_bus.py          # 事件总线
│   │   └── scheduler.py          # 任务调度
│   ├── mod_client/               # Mod 通信客户端
│   │   ├── client.py             # HTTP 客户端
│   │   ├── ws_client.py          # WebSocket 客户端
│   │   └── models.py             # 数据模型
│   ├── game/
│   │   ├── perception.py         # 状态感知
│   │   ├── inventory.py          # 背包管理
│   │   ├── actions.py            # 动作执行
│   │   ├── action_queue.py       # 动作队列
│   │   ├── chat.py               # 聊天交互
│   │   └── pathfinding.py        # 寻路算法
│   ├── skills/
│   │   ├── dsl_parser.py         # DSL 解析器
│   │   ├── runtime.py            # Skill 运行时
│   │   ├── storage.py            # Skill 存储
│   │   ├── matcher.py            # 意图匹配
│   │   └── validator.py          # DSL 校验
│   ├── ai/
│   │   ├── provider.py           # AI 提供商
│   │   ├── generator.py          # DSL 生成
│   │   ├── takeover.py           # 紧急接管
│   │   └── auto_repair.py        # 自动修复
│   ├── safety/
│   │   ├── gateway.py            # 安全入口
│   │   ├── risk_assessor.py      # 风险评估
│   │   ├── authorizer.py         # 授权管理
│   │   └── audit.py              # 审计日志
│   ├── monitoring/
│   │   ├── health.py             # 健康检查
│   │   ├── fallback.py           # 降级策略
│   │   ├── circuit_breaker.py    # 熔断器
│   │   └── auto_repair.py        # 自动修复
│   ├── webui/
│   │   ├── app.py                # FastAPI 应用
│   │   ├── routes.py             # API 路由
│   │   ├── auth.py               # 认证
│   │   ├── websocket.py          # WebSocket
│   │   └── templates/            # 前端页面
│   ├── config/
│   │   └── loader.py             # 配置加载
│   └── utils/
│       └── logger.py             # 日志工具
│
├── skills/                       # Skill 文件
│   ├── builtin/                  # 内置 Skill
│   └── custom/                   # AI 生成的 Skill
│
├── config/
│   └── config.example.yaml
├── tests/                        # 测试
├── docs/                         # 文档
├── scripts/                      # 脚本
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🔌 Fabric Mod API

Mod 启动后在端口 `25580` 暴露 HTTP API。

### 状态查询

```
GET /api/status
```
```json
{
  "connected": true,
  "health": 18.5,
  "hunger": 15,
  "position": {"x": 128.5, "y": 64.0, "z": -256.3},
  "rotation": {"yaw": 45.2, "pitch": -12.5},
  "experience": 127,
  "level": 5,
  "dimension": "overworld",
  "time_of_day": 6000,
  "weather": "clear"
}
```

```
GET /api/world
```
```json
{
  "dimension": "overworld",
  "time_of_day": 6000,
  "weather": "clear",
  "difficulty": "normal",
  "day_count": 156
}
```

```
GET /api/inventory
```
```json
{
  "items": [
    {"name": "diamond_sword", "slot": 0, "count": 1, "durability": 1561, "max_durability": 1561},
    {"name": "bread", "slot": 1, "count": 32, "durability": 0, "max_durability": 0}
  ],
  "empty_slots": 34,
  "is_full": false
}
```

```
GET /api/entities?radius=32
```
```json
{
  "entities": [
    {"id": 123, "type": "zombie", "position": {"x": 130, "y": 64, "z": -258}, "health": 20.0, "hostile": true},
    {"id": 456, "type": "cow", "position": {"x": 125, "y": 64, "z": -250}, "health": 10.0, "hostile": false}
  ]
}
```

```
GET /api/blocks?radius=16&type=stone
```
```json
{
  "blocks": [
    {"position": {"x": 128, "y": 60, "z": -256}, "type": "stone"},
    {"position": {"x": 129, "y": 60, "z": -256}, "type": "stone"}
  ]
}
```

### 动作执行

```
POST /api/move
Body: {"x": 128, "y": 64, "z": -256, "sprint": false}
```
```json
{"success": true, "details": "移动完成"}
```

```
POST /api/dig
Body: {"x": 128, "y": 63, "z": -256}
```
```json
{"success": true, "details": "挖掘完成，获得 stone x1"}
```

```
POST /api/place
Body: {"item": "torch", "x": 128, "y": 64, "z": -256}
```
```json
{"success": true, "details": "放置 torch 完成"}
```

```
POST /api/attack
Body: {"entity_id": 123}
```
```json
{"success": true, "details": "攻击 zombie，造成 7.0 伤害"}
```

```
POST /api/eat
Body: {"item": "bread"}
```
```json
{"success": true, "details": "进食 bread，恢复 5 饥饿值"}
```

```
POST /api/look
Body: {"x": 130, "y": 65, "z": -258}
```
```json
{"success": true, "details": "看向目标位置"}
```

```
POST /api/chat
Body: {"message": "Hello!"}
```
```json
{"success": true, "details": "消息已发送"}
```

### WebSocket 实时事件

```
ws://localhost:25580/ws/events
```

事件格式：
```json
{"type": "chat", "data": {"player": "Steve", "message": "hi"}}
{"type": "damage", "data": {"source": "zombie", "amount": 3.0, "health": 15.0}}
{"type": "block_change", "data": {"position": {"x": 1, "y": 2, "z": 3}, "old": "air", "new": "stone"}}
{"type": "entity_spawn", "data": {"id": 789, "type": "skeleton", "position": {"x": 10, "y": 64, "z": 20}}}
{"type": "death", "data": {"reason": "fall"}}
```

---

## 🔧 核心模块

### Mod 通信客户端

```python
# src/mod_client/client.py
class ModClient:
    """Fabric Mod HTTP 客户端"""

    def __init__(self, host: str = "localhost", port: int = 25580):
        self.base_url = f"http://{host}:{port}"

    async def get_status(self) -> dict
    async def get_world(self) -> dict
    async def get_inventory(self) -> dict
    async def get_entities(self, radius: int = 32) -> dict
    async def get_blocks(self, radius: int = 32, block_type: str = None) -> dict
    async def move(self, x, y, z, sprint=False) -> dict
    async def dig(self, x, y, z) -> dict
    async def place(self, item, x, y, z) -> dict
    async def attack(self, entity_id) -> dict
    async def eat(self, item) -> dict
    async def look(self, x, y, z) -> dict
    async def chat(self, message) -> dict
```

### 状态采集器

```python
# src/game/perception.py
class StateCollector:
    """从 Mod API 采集游戏状态"""

    def __init__(self, mod_client: ModClient):
        self.mod_client = mod_client
        self._current: Optional[GameStateSnapshot] = None
        self._last: Optional[GameStateSnapshot] = None

    async def collect(self) -> GameStateSnapshot
    def has_hostile_nearby(self, radius: float = 16.0) -> bool
    def get_nearest_entity(self, entity_type: str = None) -> Optional[EntityInfo]
    def get_blocks_by_type(self, block_type: str, radius: int = 32) -> List[BlockInfo]
```

### 动作执行器

```python
# src/game/actions.py
class ActionExecutor:
    """通过 Mod API 执行游戏动作"""

    def __init__(self, mod_client: ModClient, safety_gateway=None):
        self.mod_client = mod_client
        self.safety_gateway = safety_gateway

    async def walk_to(self, x, y, z, sprint=False) -> ActionResult
    async def dig_block(self, x, y, z) -> ActionResult
    async def place_block(self, item, x, y, z) -> ActionResult
    async def attack(self, entity_id) -> ActionResult
    async def eat(self, item) -> ActionResult
    async def look_at(self, x, y, z) -> ActionResult
    async def jump(self) -> ActionResult
```

### 背包管理器

```python
# src/game/inventory.py
class InventoryManager:
    """背包管理（数据来自 Mod API）"""

    def __init__(self, mod_client: ModClient):
        self.mod_client = mod_client

    async def refresh(self) -> None
    def count(self, item_name: str) -> int
    def has_item(self, item_name: str, min_count: int = 1) -> bool
    def is_full(self) -> bool
    def get_empty_slots(self) -> int
```

### 事件总线

```python
# src/core/event_bus.py
class EventBus:
    """发布/订阅事件总线"""

    def subscribe(self, event_type: str, handler: Callable) -> None
    def unsubscribe(self, event_type: str, handler: Callable) -> None
    async def emit(self, event: Event) -> None
    def get_history(self, event_type: str = None, limit: int = 50) -> List[Event]
```

---

## 🧠 任务分类系统

> 不是所有任务都适合固化为 Skill。BlockMind 通过三维判断自动分类任务。

### 核心问题

```
一个任务传进来，凭什么判断它是"可重复"还是"动态"？
```

### 三维判断标准

| 维度 | 固定任务 | 动态任务 |
|------|----------|----------|
| **步骤** | 每次相同，可写死 | 每次不同，无法预测 |
| **输入** | ≤3 个参数（目标、位置） | 需要描述性语言 |
| **结果** | 可量化验证（物品数量） | 主观判断（美观、创意） |

### 四级分类

| 级别 | 名称 | 缓存策略 | 例子 |
|------|------|----------|------|
| **L1** | 完全固定 | 完整 Skill | 进食、存放物品 |
| **L2** | 参数化 | Skill + 变量 | 砍树（哪棵树）、挖矿（挖什么） |
| **L3** | 模板化 | 模板 + AI 填充 | 建墙（尺寸不同）、铺路（路线不同） |
| **L4** | 完全动态 | AI 每次推理 | 建房子、探索洞穴、打Boss |

### 分类流程

```
玩家指令
    │
    ▼
┌──────────────────┐
│ 1. 查固定任务库   │  精确匹配
│    "砍树" → L2   │
└────────┬─────────┘
         │ 未命中
         ▼
┌──────────────────┐
│ 2. 关键词分析     │
│ "建/设计" → L4   │
│ "砍/挖/种" → L2  │
└────────┬─────────┘
         │ 未命中
         ▼
┌──────────────────┐
│ 3. AI 判断       │  兜底
│ 步骤可预测？      │
│ 输入简单？        │
│ 结果可验证？      │
└────────┬─────────┘
         │
         ▼
    分类结果 → 路由到对应处理器
```

### 分类示例

```python
# ✅ L1 完全固定 — 步骤永远一样
"吃东西" → eat_food Skill
"整理箱子" → organize_chest Skill

# ✅ L2 参数化 — 流程固定，目标不同
"砍一棵橡树" → chop_tree Skill(target="oak_tree")
"挖铁矿" → mine_ore Skill(target="iron_ore")

# ⚠️ L3 模板化 — 结构类似，细节不同
"建一面墙" → build_wall 模板 + AI 填充(长、宽、材料、位置)
"铺一条路" → build_path 模板 + AI 填充(起点、终点、材料)

# ❌ L4 完全动态 — 每次都不同
"建个房子" → AI 完全推理（地形、材料、风格每次不同）
"探索这个洞穴" → AI 完全推理（洞穴结构每次不同）
```

### 任务路由

```python
class TaskRouter:
    """任务路由器 — 根据分类结果分发到对应处理器"""

    async def route(self, task: str):
        classification = self.classifier.classify(task)

        if classification == "L1_fixed":
            # 直接执行缓存的 Skill
            skill = self.skill_storage.get(task)
            return await self.skill_runtime.execute(skill)

        elif classification == "L2_parameter":
            # AI 填充参数，然后执行 Skill
            params = await self.ai.fill_params(task)
            skill = self.skill_storage.get(task.type)
            return await self.skill_runtime.execute(skill, params)

        elif classification == "L3_template":
            # AI 填充模板细节，然后执行
            filled = await self.ai.fill_template(task)
            return await self.skill_runtime.execute(filled)

        else:  # L4_dynamic
            # AI 完全推理，不缓存
            actions = await self.ai.reason(task)
            return await self.action_executor.execute_sequence(actions)
```

---

## 📝 Skill DSL 系统

### 语法规范

```yaml
skill_id: string      # 唯一标识
name: string          # 显示名称
tags: list[string]    # 检索标签
priority: int         # 1=最高, 5=最低
when:                 # 触发条件
  all: [expression]   # 所有条件满足
  any: [expression]   # 任意条件满足
do: [statement]       # 执行逻辑
until:                # 结束条件
  any: [expression]
```

### 内置函数

| 类别 | 函数 | 说明 |
|------|------|------|
| 状态 | `self.health()` | 生命值 |
| | `self.hunger()` | 饥饿值 |
| | `self.position()` | 当前坐标 |
| | `inventory.count(item)` | 物品数量 |
| | `world.time()` | 游戏时间 |
| | `world.any_entity(type, radius)` | 是否有实体 |
| 动作 | `walk_to(pos)` | 走到位置 |
| | `dig_block(pos)` | 挖掘方块 |
| | `place_block(item, pos)` | 放置方块 |
| | `attack(entity)` | 攻击实体 |
| | `eat(item)` | 进食 |
| 控制 | `if/then/else` | 条件 |
| | `loop/while` | 循环 |
| | `break_loop()` | 跳出 |
| | `wait(seconds)` | 等待 |

### 示例：砍树

```yaml
skill_id: skill_chop_tree_001
name: 砍树
tags: ["砍树", "收集木材"]
priority: 4

when:
  all:
    - "inventory.has('wooden_axe') or inventory.has('stone_axe')"
    - "world.any_entity(type='oak_tree', radius=32)"

do:
  - scan_entities:
      radius: 32
      filter: "type == 'oak_tree'"
      sort_by: distance
  - walk_to: "scanned_entities[0].position"
  - loop:
      while: "world.entity_exists(scanned_entities[0].id)"
      do:
        - dig_block: "scanned_entities[0].position"
        - wait: 1

until:
  any:
    - "inventory.count('oak_log') >= 64"
    - "task_interrupted()"
```

---

## 🛡️ 安全体系

### 操作风险等级

| 等级 | 操作 | 策略 |
|------|------|------|
| 0 | 移动、跳跃、聊天 | 自动执行 |
| 1 | 挖泥土、放火把 | 自动执行 |
| 2 | 挖矿石、攻击中立生物 | 自动执行 |
| 3 | 点燃TNT、放岩浆、开箱子 | 需玩家授权 |
| 4 | 放命令方块、自杀 | 默认禁止 |

### 玩家远程指令

| 指令 | 功能 |
|------|------|
| `!stop` | 终止所有任务 |
| `!come` | 传送到玩家身边 |
| `!safe` | 回安全点 |
| `!status` | 查看状态 |
| `!approve` | 同意高风险操作 |
| `!deny` | 拒绝高风险操作 |
| `!disable_ai` | 禁用 AI 接管 |
| `!enable_ai` | 启用 AI 接管 |

---

## 🔥 故障容错

### 三级降级

```
1级（临时偶发）→ 自动重试 3 次
2级（无法恢复）→ 终止任务，返回安全点
3级（危及安全）→ 紧急熔断 + AI 实时接管
```

### AI 紧急接管

```
【紧急接管模式】
首要任务：保证机器人安全
规则：只输出动作指令，优先处理：溺水>被攻击>掉落
安全后输出 "SAFE"
```

---

## 🤖 空闲自主任务系统

### 触发条件

```
✅ 无玩家指令
✅ 无危险（无敌对生物，血量 > 50%）
✅ 无待执行任务
→ 进入空闲模式
```

### 任务池

| 任务 | 描述 | 优先级 |
|------|------|--------|
| 🌾 自动种田 | 播种→收割→补种 | 5 |
| ⛏️ 自主挖矿 | 挖掘铁矿/煤矿 | 5 |
| 🌲 自主砍树 | 收集木材 | 5 |
| 📦 整理箱子 | 分类存放 | 5 |
| 🏠 修补房屋 | 修复建筑 | 4 |
| 🔦 点亮区域 | 放火把防怪 | 4 |
| 🚶 巡逻区域 | 巡视基地 | 5 |

---

## 🖥️ WebUI 控制面板

| 页面 | 功能 |
|------|------|
| 📊 仪表盘 | 状态卡片、任务进度、快捷操作 |
| 🛠️ Skill管理 | 浏览/编辑/测试 Skill |
| 🛡️ 安全设置 | 风险等级、授权策略 |
| 📋 日志中心 | 日志查询、统计 |
| ⚙️ 系统设置 | 服务器/AI/WebUI 配置 |
| 🔌 连接状态 | Mod/AI/WebUI 状态 |

---

## ⚙️ 配置参考

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `mod.host` | string | localhost | Mod HTTP 地址 |
| `mod.port` | int | 25580 | Mod HTTP 端口 |
| `game.server_ip` | string | - | MC 服务器地址 |
| `game.server_port` | int | 25565 | MC 服务器端口 |
| `ai.provider` | string | openai | AI 提供商 |
| `ai.model` | string | gpt-4o | AI 模型 |
| `webui.port` | int | 8080 | WebUI 端口 |
| `safety.auth_timeout` | int | 30 | 授权等待超时 |
| `idle_tasks.enabled` | bool | true | 空闲任务开关 |

---

## 🚀 部署指南

### Systemd 部署

```bash
# 安装 Mod
cp mod/build/libs/blockmind-mod-1.0.0.jar /opt/mc-server/mods/

# 部署 Python 后端
sudo bash scripts/deploy.sh

# 服务管理
sudo systemctl start blockmind
sudo systemctl status blockmind
journalctl -u blockmind -f
```

### Docker 部署

```bash
docker-compose up -d
```

---

## 👨‍💻 开发指南

```bash
# 本地开发
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 测试
pytest tests/ -v

# Mod 开发
cd mod && ./gradlew build
```

---

## ❓ FAQ

**Q: 必须用 Fabric 吗？**
A: 是的。pyCraft 不支持 1.20+，Fabric Mod 是最可靠的方案。

**Q: 支持离线服务器吗？**
A: 支持。Mod 不验证正版，Python 端配置 `auth_mode: offline`。

**Q: Mod 会影响服务器性能吗？**
A: 几乎不影响。Mod 只暴露 API，不做额外计算。

---

## 🗺️ 路线图

### v2.0（当前）
- [x] Fabric Mod + HTTP API
- [x] Skill DSL 系统
- [x] AI 决策 + 自动修复
- [x] 安全校验
- [x] WebUI 控制面板

### v2.1
- [ ] Mod 可视化配置
- [ ] Skill 市场
- [ ] 多机器人协同

---

## 📄 许可证

MIT License

---

<p align="center">
  <i>🧠 BlockMind — Every block has a mind.</i>
</p>
