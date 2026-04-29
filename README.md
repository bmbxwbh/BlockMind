# 🎮 BlockMind — 智能 Minecraft AI 玩伴系统

> **Skill 固化复用版** · v1.0 · 2026-04-29

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![MC](https://img.shields.io/badge/Minecraft-1.19.x--1.21.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)

**一句话概括：** 部署在云服务器上的 7×24 小时 Minecraft AI 玩伴，具备自主生存、智能交互、Skill 技能固化复用能力。

---

## 📖 目录

- [项目特色](#-项目特色)
- [系统架构](#-系统架构)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [核心模块](#-核心模块)
- [Skill DSL 系统](#-skill-dsl-系统)
- [安全体系](#-安全体系)
- [故障容错](#-故障容错)
- [空闲自主任务](#-空闲自主任务系统)
- [WebUI 控制面板](#-webui-控制面板)
- [部署指南](#-部署指南)
- [开发指南](#-开发指南)
- [常见问题](#-常见问题)
- [路线图](#-路线图)

---

## ✨ 项目特色

### 🧠 Skill DSL 固化复用 —— 核心创新

```
传统方式：  玩家指令 → AI 思考 → 执行 → 下次再思考（每次消耗 Token）
Skill 方式：玩家指令 → AI 思考 → 生成 Skill → 执行 → 永久复用（零 Token）
```

AI 决策一次，生成 DSL Skill 文件，之后 **零 token 反复执行**。就像给机器人学会了"肌肉记忆"，不需要每次都重新思考。

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

```
┌─────────────────────────────────────────────────────┐
│                   WebUI 控制面板                     │
│          状态监控 · Skill管理 · 安全配置              │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│                   游戏交互层                         │
│     机器人接入 · 动作执行 · 聊天交互 · 状态感知       │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│                 全局安全校验层                        │
│        所有动作统一入口 · 风险判断 · 授权控制          │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│                   机器人控制层                        │
│          动作指令解析 · MC API 调用                   │
└───────────┬───────────────────────┬─────────────────┘
            │                       │
┌───────────▼───────────┐ ┌────────▼─────────────────┐
│    Skill 调度层        │ │      AI 决策层            │
│  意图解析 · Skill匹配  │ │  自然语言→DSL · 紧急接管  │
│  任务调度 · 决策路由    │ │                          │
└───────────┬───────────┘ └────────┬─────────────────┘
            │                       │
┌───────────▼───────────────────────▼─────────────────┐
│                  Skill 运行时引擎                     │
│     DSL解析 · 状态管理 · 控制流调度 · 动作执行        │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│                    Skill 存储层                      │
│       Skill文件管理 · 检索 · 更新 · 版本控制          │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│               故障监控与降级模块                      │
│     错误检测 · 紧急熔断 · AI接管 · Skill自动修复      │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│                    运维保障层                         │
│         系统部署 · 进程守护 · 日志监控                │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求

- **操作系统**：Ubuntu 22.04 LTS（推荐）
- **Python**：3.9+
- **Minecraft**：1.19.x - 1.21.x（正版/离线模式）
- **内存**：≥ 2GB
- **磁盘**：≥ 10GB

### 安装

```bash
# 1. 克隆项目
git clone https://github.com/your-username/BlockMind.git
cd BlockMind

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置（首次运行会自动生成配置文件）
cp config.example.yaml config.yaml
# 编辑 config.yaml 填入你的配置

# 5. 启动
python -m src.main
```

### 最小配置

```yaml
# config.yaml
game:
  server_ip: "your-server.com"
  server_port: 25565
  username: "AI_Companion"
  version: "1.20.4"

ai:
  provider: "openai"  # 或 anthropic / local
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
├── src/
│   ├── core/               # 核心引擎
│   │   ├── engine.py       # 主引擎入口
│   │   ├── scheduler.py    # 任务调度器
│   │   └── event_bus.py    # 事件总线
│   ├── game/               # 游戏交互层
│   │   ├── connection.py   # MC 服务器连接
│   │   ├── actions.py      # 动作执行器
│   │   ├── perception.py   # 环境感知
│   │   └── chat.py         # 聊天交互
│   ├── skills/             # Skill 系统
│   │   ├── dsl_parser.py   # DSL 解析器
│   │   ├── runtime.py      # Skill 运行时引擎
│   │   ├── storage.py      # Skill 存储管理
│   │   └── matcher.py      # Skill 意图匹配
│   ├── ai/                 # AI 决策层
│   │   ├── provider.py     # AI 模型适配器
│   │   ├── generator.py    # DSL 生成器
│   │   ├── validator.py    # DSL 校验器
│   │   └── takeover.py     # 紧急接管模块
│   ├── safety/             # 安全校验层
│   │   ├── risk_assessor.py    # 风险评估
│   │   ├── authorizer.py       # 授权管理
│   │   ├── permission.py       # 权限控制
│   │   └── audit.py            # 审计日志
│   ├── monitoring/         # 故障监控
│   │   ├── health.py       # 健康检查
│   │   ├── fallback.py     # 降级策略
│   │   ├── alerter.py      # 告警通知
│   │   └── auto_repair.py  # 自动修复
│   ├── webui/              # WebUI 控制面板
│   │   ├── app.py          # Flask/FastAPI 应用
│   │   ├── routes.py       # API 路由
│   │   ├── auth.py         # 登录认证
│   │   ├── websocket.py    # 实时推送
│   │   └── templates/      # 前端页面
│   │       ├── dashboard.html
│   │       ├── skills.html
│   │       ├── safety.html
│   │       ├── logs.html
│   │       └── settings.html
│   ├── config/             # 配置管理
│   │   ├── loader.py       # 配置加载
│   │   └── schema.py       # 配置校验
│   └── utils/              # 工具函数
│       ├── logger.py       # 日志工具
│       ├── retry.py        # 重试机制
│       └── format.py       # 格式化工具
├── skills/
│   ├── builtin/            # 内置 Skill（15+）
│   │   ├── survival/       # 生存类
│   │   ├── gathering/      # 采集类
│   │   ├── building/       # 建造类
│   │   └── farming/        # 农业类
│   └── custom/             # AI 生成的自定义 Skill
├── config/                 # 配置文件
│   ├── config.example.yaml # 配置模板
│   ├── security.yaml       # 安全规则
│   └── skills.yaml         # Skill 配置
├── tests/                  # 测试
├── scripts/                # 脚本
│   ├── deploy.sh           # 部署脚本
│   └── setup.sh            # 环境配置
├── docs/                   # 文档
├── requirements.txt        # Python 依赖
├── Dockerfile              # Docker 支持
├── docker-compose.yml
└── README.md
```

---

## 🔧 核心模块

### 1. 游戏连接模块

```python
class MCConnection:
    """MC 服务器连接管理"""

    async def connect(self, server_ip: str, port: int, username: str) -> bool
    async def disconnect(self) -> None
    async def send_chat(self, message: str) -> None
    async def get_world_state(self) -> WorldState
    async def get_entity_state(self, entity_id: int) -> EntityState
    async def get_inventory(self) -> List[Item]
    async def execute_action(self, action: Action) -> ActionResult
```

**特性：**
- 异步连接管理，支持断线自动重连
- 实时状态同步：地形、怪物、物资、玩家
- 支持正版/离线模式
- 适配 MC 1.19.x - 1.21.x

### 2. Skill DSL 运行时引擎

```python
class SkillRuntime:
    """Skill 执行引擎"""

    def __init__(self, mc_connection: MCConnection):
        self.dsl_parser = DSLParser()
        self.state_manager = StateManager(mc_connection)
        self.action_executor = ActionExecutor(mc_connection)
        self.control_flow = ControlFlowScheduler()

    async def execute_skill(self, skill_path: str) -> SkillResult:
        skill = self.dsl_parser.parse(skill_path)
        await self.state_manager.update()
        return await self.control_flow.run(skill, self.state_manager, self.action_executor)
```

### 3. AI 决策模块

```python
class AIDecider:
    """AI 决策与 DSL 生成"""

    async def generate_skill(self, task_description: str) -> SkillDSL:
        """将自然语言任务转换为 DSL Skill"""

    async def validate_skill(self, skill: SkillDSL) -> ValidationResult:
        """校验 DSL 语法和安全性"""

    async def emergency_takeover(self, context: dict) -> List[Action]:
        """紧急接管模式，直接控制机器人"""
```

---

## 📝 Skill DSL 系统

### 语法规范

```yaml
# skills/builtin/survival/chop_tree.yaml
skill_id: skill_chop_tree_001
name: 砍树
tags: ["砍树", "收集木材", "生存"]
priority: 4  # 1=最高, 5=最低

# 触发条件
when:
  all:
    - inventory.count("wooden_axe") > 0
    - world.any_entity(type="oak_tree")
    - not has_higher_priority_task()

# 执行逻辑
do:
  - scan_entities:
      radius: 32
      filter:
        type: oak_tree
      sort_by: distance

  - walk_to: scanned_entities[0].position

  - loop:
      while: world.entity_exists(scanned_entities[0].id)
      do:
        - dig_block: scanned_entities[0].position

  - scan_drops:
      radius: 5

  - loop:
      over: scanned_drops
      do:
        - walk_to: item.position
        - pickup_item: item

# 结束条件
until:
  any:
    - inventory.count("oak_log") >= 64
    - not world.any_entity(type="oak_tree")
    - task_interrupted()
```

### 内置函数库

| 类别 | 函数 | 说明 |
|------|------|------|
| **状态查询** | `self.health()` | 当前生命值 |
| | `self.hunger()` | 当前饥饿值 |
| | `self.position()` | 当前坐标 |
| | `inventory.count(item)` | 物品数量 |
| | `world.time()` | 游戏时间 |
| | `world.get_block(pos)` | 方块类型 |
| **动作函数** | `walk_to(pos)` | 走到指定位置 |
| | `dig_block(pos)` | 挖掘方块 |
| | `place_block(item, pos)` | 放置方块 |
| | `attack(entity)` | 攻击实体 |
| | `eat(item)` | 吃食物 |
| | `look_at(pos)` | 看向位置 |
| **控制流** | `if/then/else` | 条件判断 |
| | `loop` | 循环执行 |
| | `break_loop()` | 跳出循环 |
| | `wait(seconds)` | 等待 |
| **工具函数** | `scan_blocks(center, radius, filter)` | 扫描方块 |
| | `scan_entities(radius, filter)` | 扫描实体 |
| | `sort(list, by)` | 排序 |
| | `filter(list, condition)` | 过滤 |

### 内置 Skill 库（15+）

```
skills/builtin/
├── survival/
│   ├── emergency_retreat.yaml    # 紧急撤退
│   ├── eat_food.yaml             # 自动吃食物
│   └── avoid_hostile.yaml        # 躲避敌对生物
├── gathering/
│   ├── chop_tree.yaml            # 砍树
│   ├── mine_stone.yaml           # 挖石头
│   ├── mine_ore.yaml             # 挖矿石
│   └── collect_crops.yaml        # 收集作物
├── building/
│   ├── build_shelter.yaml        # 建造庇护所
│   ├── place_torches.yaml        # 放置火把
│   └── repair_building.yaml      # 修补建筑
├── farming/
│   ├── plant_wheat.yaml          # 种植小麦
│   ├── harvest_wheat.yaml        # 收割小麦
│   └── replant.yaml              # 重新种植
└── storage/
    ├── organize_chest.yaml       # 整理箱子
    └── deposit_items.yaml        # 存放物品
```

---

## 🛡️ 安全体系

### 操作风险等级

| 等级 | 名称 | 示例操作 | 授权策略 |
|------|------|----------|----------|
| **0** | 完全安全 | 移动、跳跃、聊天 | 自动执行 |
| **1** | 低风险 | 挖泥土、放火把、捡物品 | 自动执行 |
| **2** | 中风险 | 挖矿石、攻击中立生物 | 自动执行 |
| **3** | 高风险 | 点燃TNT、放岩浆、开箱子 | 需玩家授权 |
| **4** | 致命风险 | 放命令方块、自杀 | 默认禁止 |

### 安全配置

```yaml
# config/security.yaml
global_settings:
  default_timeout: 60
  default_timeout_action: deny
  enable_audit_log: true
  max_application_frequency: 1

operation_risk_levels:
  move: 0
  jump: 0
  chat: 0
  break_dirt: 1
  place_torch: 1
  break_ore: 2
  attack_neutral: 2
  ignite_tnt: 3
  place_lava: 3
  break_chest: 3
  suicide: 4
  place_command_block: 4
```

### 玩家远程指令

在游戏聊天框发送以下指令控制机器人：

| 指令 | 功能 |
|------|------|
| `!stop` | 立即终止所有任务，返回安全点 |
| `!come` | 传送到玩家身边 |
| `!safe` | 强制传送回出生点/床边 |
| `!status` | 查看机器人当前状态 |
| `!approve` | 同意高风险操作 |
| `!deny` | 拒绝高风险操作 |
| `!disable_ai` | 禁用 AI 自动接管 |
| `!enable_ai` | 启用 AI 自动接管 |
| `!skill list` | 列出所有可用 Skill |
| `!skill run <name>` | 手动执行指定 Skill |

---

## 🔥 故障容错

### 三级降级机制

```
┌──────────────────────────────────────────────────────┐
│  1级错误（临时偶发）                                   │
│  处理：自动重试 3 次                                   │
│  告警：§e[提示] 正在自动重试...                        │
├──────────────────────────────────────────────────────┤
│  2级错误（无法恢复但安全）                              │
│  处理：终止任务，返回安全点                             │
│  告警：§6[警告] 任务已终止，返回安全点                  │
├──────────────────────────────────────────────────────┤
│  3级错误（危及安全）                                   │
│  处理：紧急熔断 → AI 实时接管 → 修复 Skill             │
│  告警：§c§l[紧急告警] AI 已接管控制！                   │
└──────────────────────────────────────────────────────┘
```

### AI 紧急接管

当触发 3 级错误时，AI 直接接管机器人控制：

```
【紧急接管模式启动】
你现在直接控制 Minecraft 机器人，当前处于紧急危险状态。
首要任务是保证机器人安全。

【规则】
1. 只输出动作指令，不要输出任何解释
2. 可用指令：walk_to(x,y,z), jump(), dig(), attack(entity_id), eat(item)
3. 优先处理：溺水 > 被攻击 > 掉落 > 其他
4. 安全后输出 "SAFE"

【当前状态】
{context_snapshot}
```

### 自动修复

故障恢复后，AI 自动分析错误原因并修复对应的 Skill DSL：

```python
async def auto_repair_skill(failed_skill: SkillDSL, error: Exception) -> SkillDSL:
    """AI 自动修复出错的 Skill"""
    analysis = await ai.analyze_error(failed_skill, error)
    fixed_skill = await ai.fix_skill(failed_skill, analysis)
    validation = await validator.validate(fixed_skill)
    if validation.passed:
        storage.replace(failed_skill.skill_id, fixed_skill)
        return fixed_skill
```

---

## 🤖 空闲自主任务系统

> 当没有玩家指令、没有危险、没有待执行任务时，机器人自动进入"自由活动"模式，像真人玩家一样自主生存。

### 触发条件

```
┌──────────────────────────────────────────────────────┐
│  空闲状态判定（三个条件同时满足）                       │
│                                                      │
│  ✅ 无玩家指令（最近 N 秒内无 ! 前缀指令）             │
│  ✅ 无危险（附近无敌对生物，血量 > 50%）               │
│  ✅ 无待执行任务（当前任务队列为空）                    │
│                                                      │
│  → 进入空闲模式，从任务池中选择下一个任务               │
└──────────────────────────────────────────────────────┘
```

### 空闲任务池

| 优先级 | 任务名称 | 描述 | 预估耗时 |
|--------|----------|------|----------|
| 5 | 🌾 自动种田 | 播种 → 等待成熟 → 收割 → 重新种植 | 2-5 分钟 |
| 5 | ⛏️ 自主挖矿 | 寻找矿脉，挖掘铁矿/煤矿/金矿 | 3-8 分钟 |
| 5 | 🌲 自主砍树 | 收集木材，补充建筑材料 | 1-3 分钟 |
| 5 | 📦 整理箱子 | 将背包物品分类存入储物箱 | 1-2 分钟 |
| 5 | 🏠 修补房屋 | 修复被破坏的方块，填补缺口 | 2-5 分钟 |
| 4 | 🔦 点亮区域 | 在黑暗处放置火把，防止怪物生成 | 1-3 分钟 |
| 5 | 🚶 巡逻区域 | 在基地周围巡视，标记资源点 | 3-5 分钟 |
| 5 | 💰 存放物资 | 背包满时自动回仓存放 | 1 分钟 |

### 调度逻辑

```python
class IdleTaskScheduler:
    """
    空闲任务调度器
    
    调度策略：
    1. 每个任务执行完成后休息 30 秒（可配置）
    2. 从任务池中按优先级 + 随机组合选择下一个任务
    3. 优先级相同的任务随机轮转，避免单一重复
    4. 支持通过配置文件开启/关闭每种自主行动
    5. 执行过程中如果收到玩家指令，立即中断当前任务
    """

    async def schedule_loop(self):
        """主调度循环"""
        while self.running:
            if self._is_idle():
                task = self._select_task()
                await self._execute_with_interrupt(task)
                await asyncio.sleep(self.config.idle_tasks.interval)
            else:
                await asyncio.sleep(5)  # 非空闲状态，5秒后再检查
```

### 配置项

```yaml
# config.yaml
idle_tasks:
  enabled: true              # 总开关
  interval: 30               # 任务间休息间隔（秒）

  actions:
    - name: "farm_wheat"
      enabled: true          # 可单独关闭某种任务
      priority: 5
    - name: "mine_resources"
      enabled: true
      priority: 5
    - name: "chop_tree"
      enabled: true
      priority: 5
    - name: "organize_chest"
      enabled: true
      priority: 5
    - name: "repair_building"
      enabled: true
      priority: 4
    - name: "place_torches"
      enabled: true
      priority: 4
    - name: "patrol_area"
      enabled: false         # 默认关闭巡逻
      priority: 5
    - name: "deposit_items"
      enabled: true
      priority: 5
```

### 自主行为示例

```
[14:00:00] 🤖 进入空闲模式
[14:00:01] 🌾 选择任务：自动种田
[14:00:03] 🚶 走向农田 (128, 64, -256)
[14:00:08] 🌱 开始播种... 已播种 12/16 格
[14:00:15] ✅ 播种完成，休息 30 秒...
[14:00:45] 🤖 选择任务：整理箱子
[14:00:47] 🚶 走向储物室 (130, 64, -260)
[14:00:52] 📦 开始整理... 钻石×3 → 矿石箱
[14:00:58] 📦 木头×16 → 木材箱
[14:01:02] ✅ 整理完成，休息 30 秒...
[14:01:32] ⚠️ 检测到玩家指令 "!come"，中断空闲任务
[14:01:33] 🚶 前往玩家身边...
```

---

## 🖥️ WebUI 控制面板

### 功能概览

WebUI 提供可视化管理界面，基于 **FastAPI + Vue.js** 构建，支持实时 WebSocket 推送。

```
┌─────────────────────────────────────────────────────────────┐
│  🎮 MC AI Companion · WebUI                                 │
├─────────┬───────────────────────────────────────────────────┤
│         │                                                   │
│ 📊 仪表盘 │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│         │  │ ❤️ 生命值     │ │ 🍖 饥饿值    │ │ 📍 位置      ││
│ 🛠️ Skills│  │   18/20     │  │   15/20     │  │ 128,64,-256 ││
│         │  └─────────────┘ └─────────────┘ └─────────────┘│
│ 🛡️ 安全  │                                                   │
│         │  ┌─────────────────────────────────────────────┐ │
│ 📋 日志  │  │  当前任务：砍树                              │ │
│         │  │  ████████████░░░░░░ 65%                    │ │
│ ⚙️ 设置  │  │  状态：执行中 · 已收集 42/64 木头            │ │
│         │  └─────────────────────────────────────────────┘ │
│ 🔌 连接  │                                                   │
│         │  ┌─────────────────────────────────────────────┐ │
│         │  │  📜 实时日志                                  │ │
│         │  │  [15:30:22] ✅ 找到橡树 (距离 12m)           │ │
│         │  │  [15:30:25] 🚶 正在走向目标...               │ │
│         │  │  [15:30:28] ⛏️ 开始挖掘...                   │ │
│         │  │  [15:30:31] ✅ 获得橡木 x4                  │ │
│         │  └─────────────────────────────────────────────┘ │
└─────────┴───────────────────────────────────────────────────┘
```

### 页面设计

#### 1. 📊 仪表盘 (Dashboard)

实时展示机器人状态：

| 区域 | 内容 |
|------|------|
| **状态卡片** | 生命值、饥饿值、当前位置、游戏时间 |
| **任务面板** | 当前任务名称、进度条、执行时长 |
| **快捷操作** | 🏠 回家、⏹️ 停止、🔄 重连、📸 截图 |
| **资源概览** | 背包物品统计、已收集资源 |
| **实时日志** | 最近 50 条操作日志，可筛选级别 |

#### 2. 🛠️ Skill 管理

```
┌─────────────────────────────────────────────────────────────┐
│  Skill 管理                                    [+ 新建 Skill] │
├─────────────────────────────────────────────────────────────┤
│  🔍 搜索 Skill...        [全部] [内置] [自定义] [禁用]       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🌲 砍树 (skill_chop_tree_001)              [编辑] [禁用]│   │
│  │    标签：砍树 · 收集木材 · 生存                       │   │
│  │    优先级：4 · 使用次数：127 · 成功率：98.4%          │   │
│  │    最后执行：2026-04-29 15:30                       │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🌾 种植小麦 (skill_plant_wheat_001)        [编辑] [禁用]│   │
│  │    标签：种田 · 农业 · 生存                           │   │
│  │    优先级：5 · 使用次数：89 · 成功率：100%            │   │
│  │    最后执行：2026-04-29 14:15                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**功能：**
- 浏览/搜索/筛选所有 Skill
- 在线编辑 DSL（语法高亮 + 实时校验）
- 启用/禁用 Skill
- 查看使用统计（次数、成功率、耗时）
- 手动触发执行
- 导入/导出 Skill 文件
- 版本历史（回滚到之前的版本）

#### 3. 🛡️ 安全设置

```
┌─────────────────────────────────────────────────────────────┐
│  安全设置                                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📋 操作风险等级配置                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  操作           │ 风险等级  │ 授权策略                │   │
│  │─────────────────│──────────│───────────────────────│   │
│  │  移动/跳跃       │ 0-安全   │ 自动执行               │   │
│  │  挖掘(泥土)      │ 1-低     │ 自动执行               │   │
│  │  挖掘(矿石)      │ 2-中     │ 自动执行               │   │
│  │  点燃TNT    [▼] │ 3-高  [▼]│ 需玩家授权        [▼]  │   │
│  │  放命令方块 [▼]  │ 4-致命[▼]│ 默认禁止          [▼]  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  🚨 高风险操作等待授权                                       │
│  等待超时时间：[30] 秒    超时动作：[拒绝 ▼]                  │
│                                                             │
│  📝 审计日志                                                 │
│  [x] 启用审计日志     保留天数：[30] 天                       │
│                                                             │
│  🤖 AI 自动接管                                              │
│  [x] 启用紧急自动接管    接管后自动修复 Skill                  │
│                                                             │
│  [保存设置]  [恢复默认]                                       │
└─────────────────────────────────────────────────────────────┘
```

**功能：**
- 可视化编辑操作风险等级
- 配置授权策略（自动/需授权/禁止）
- 设置授权等待超时
- 开关审计日志
- 配置 AI 紧急接管参数
- 查看授权历史记录

#### 4. 📋 日志中心

```
┌─────────────────────────────────────────────────────────────┐
│  日志中心                                                    │
├─────────────────────────────────────────────────────────────┤
│  [全部] [INFO] [WARN] [ERROR] [安全] [执行]                  │
│  🔍 搜索日志...        时间范围：[今天 ▼]                     │
├─────────────────────────────────────────────────────────────┤
│  [15:30:22] [INFO ] [Security] 高风险操作申请：ignite_tnt    │
│  [15:30:35] [INFO ] [Security] 玩家同意执行操作              │
│  [15:30:36] [INFO ] [Action  ] 操作执行成功                  │
│  [15:31:02] [WARN ] [Monitor ] 生命值过低 (5/20)            │
│  [15:31:05] [ERROR] [Skill   ] 砍树技能执行失败              │
│  [15:31:06] [INFO ] [Fallback] 触发2级降级，返回安全点       │
├─────────────────────────────────────────────────────────────┤
│  📊 日志统计：今日 INFO 1,247 · WARN 23 · ERROR 3           │
│  [导出日志]  [清除日志]                                       │
└─────────────────────────────────────────────────────────────┘
```

#### 5. ⚙️ 系统设置

```
┌─────────────────────────────────────────────────────────────┐
│  系统设置                                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🔌 服务器连接                                               │
│  服务器地址：[your-server.com        ]                       │
│  端口：[25565]  MC版本：[1.20.4 ▼]                           │
│  用户名：[AI_Companion           ]                           │
│  认证模式：[离线 ▼]                                          │
│  [x] 断线自动重连    重连间隔：[5] 秒    最大重试：[∞]       │
│                                                             │
│  🤖 AI 模型配置                                              │
│  提供商：[OpenAI ▼]  模型：[gpt-4o ▼]                        │
│  API Key：[••••••••••••••••]  [显示]                         │
│  API地址：[https://api.openai.com/v1]                        │
│  Temperature：[0.7]  Max Tokens：[4096]                      │
│  [x] 启用流式输出    [x] 启用思考模式                         │
│                                                             │
│  🎮 游戏行为                                                 │
│  [x] 启用空闲自主行动                                        │
│  自主任务间隔：[30] 秒                                       │
│  自主行动类型：[✓种田] [✓挖矿] [✓整理] [✓巡逻]              │
│                                                             │
│  📡 WebUI                                                   │
│  [x] 启用 WebUI    端口：[8080]                              │
│  管理密码：[••••••••]                                        │
│  [x] 允许远程访问    允许IP：[0.0.0.0/0]                     │
│                                                             │
│  💾 数据与存储                                               │
│  Skill存储路径：[/data/skills]                               │
│  日志保留天数：[30]    最大日志大小：[100MB]                  │
│  [x] 启用 Skill 版本控制                                     │
│                                                             │
│  [保存设置]  [恢复默认]  [导出配置]  [导入配置]               │
└─────────────────────────────────────────────────────────────┘
```

#### 6. 🔌 连接状态

```
┌─────────────────────────────────────────────────────────────┐
│  连接状态                                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🟢 MC 服务器    已连接 · 延迟 23ms                          │
│  服务器：hypixel.net:25565                                   │
│  在线玩家：12/100                                            │
│  世界：overworld · 时间：Day 156 · 天气：Clear               │
│                                                             │
│  🟢 AI 模型     已连接 · 余额 $12.34                         │
│  模型：gpt-4o · 今日调用：234次 · Token：45,678              │
│                                                             │
│  🟢 WebUI       运行中 · http://0.0.0.0:8080                │
│  活跃连接：2 · 总访问：156次                                  │
│                                                             │
│  📊 资源监控                                                 │
│  CPU：12%  内存：340MB/2GB  磁盘：2.1GB/10GB  网络：↑2KB/s ↓5KB/s│
│                                                             │
│  [重连服务器]  [重启AI]  [重启WebUI]                         │
└─────────────────────────────────────────────────────────────┘
```

### WebUI API 接口

```python
# RESTful API
GET    /api/status              # 获取机器人状态
GET    /api/skills              # 获取 Skill 列表
POST   /api/skills              # 创建新 Skill
PUT    /api/skills/{id}         # 更新 Skill
DELETE /api/skills/{id}         # 删除 Skill
POST   /api/skills/{id}/run     # 手动执行 Skill
GET    /api/logs                # 获取日志
GET    /api/safety/rules        # 获取安全规则
PUT    /api/safety/rules        # 更新安全规则
POST   /api/safety/approve/{id} # 授权操作
GET    /api/config              # 获取配置
PUT    /api/config              # 更新配置
POST   /api/action/{command}    # 发送远程指令

# WebSocket
WS     /ws/live                 # 实时状态推送
WS     /ws/logs                 # 实时日志流
WS     /ws/task                 # 任务进度推送
```

---

## 🚀 部署指南

### 方式一：Systemd 部署（推荐）

```bash
# 运行部署脚本
sudo bash scripts/deploy.sh

# 服务管理
sudo systemctl start mc-ai-companion     # 启动
sudo systemctl stop mc-ai-companion      # 停止
sudo systemctl restart mc-ai-companion   # 重启
sudo systemctl status mc-ai-companion    # 查看状态
journalctl -u mc-ai-companion -f         # 查看日志
```

### 方式二：Docker 部署

```bash
# 使用 docker-compose
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### Systemd 服务配置

```ini
# /etc/systemd/system/mc-ai-companion.service
[Unit]
Description=Minecraft AI Companion Service
After=network.target

[Service]
Type=simple
User=mc-ai
WorkingDirectory=/opt/BlockMind
ExecStart=/opt/BlockMind/venv/bin/python -m src.main
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# 资源限制
MemoryMax=1G
CPUQuota=50%

[Install]
WantedBy=multi-user.target
```

---

## 👨‍💻 开发指南

### 本地开发

```bash
# 克隆并安装
git clone https://github.com/your-username/BlockMind.git
cd BlockMind
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖

# 运行测试
pytest tests/ -v

# 代码检查
ruff check src/
mypy src/
```

### 编写自定义 Skill

```yaml
# skills/custom/my_skill.yaml
skill_id: custom_my_skill_001
name: 我的自定义技能
tags: ["自定义", "示例"]
priority: 3

when:
  all:
    - self.health() > 10
    - inventory.count("diamond") < 64

do:
  - walk_to: { x: 100, y: 64, z: -200 }
  - dig_block: { x: 100, y: 63, z: -200 }
  - wait: 2

until:
  any:
    - inventory.count("diamond") >= 64
    - task_interrupted()
```

### 测试 Skill DSL

```bash
# 语法检查
python -m src.skills.dsl_parser validate skills/custom/my_skill.yaml

# 模拟执行（不连接服务器）
python -m src.skills.runtime dry-run skills/custom/my_skill.yaml

# 实际执行
python -m src.skills.runtime run skills/custom/my_skill.yaml
```

---

## ❓ 常见问题

### Q: 支持哪些 Minecraft 版本？
**A:** 支持 1.19.x 到 1.21.x，包括正版和离线模式。

### Q: AI 模型有推荐吗？
**A:** 推荐使用 GPT-4o 或 Claude 3.5 Sonnet，效果最好。也可以使用本地部署的开源模型（如 Qwen-72B），但需要足够的 GPU 显存。

### Q: Skill 执行失败会怎样？
**A:** 系统会根据错误级别自动处理：1级自动重试，2级终止回安全点，3级 AI 紧急接管。所有失败都会记录日志。

### Q: 可以同时控制多个机器人吗？
**A:** 当前版本支持单机器人。多 AI 协同功能已在路线图中，将在 v2.0 实现。

### Q: WebUI 安全吗？
**A:** WebUI 支持密码认证，建议仅在内网使用。如需公网访问，建议配合 Nginx 反向代理 + HTTPS。

### Q: 如何备份 Skill？
**A:** 所有 Skill 文件存储在 `skills/custom/` 目录，支持 Git 版本控制。也可以在 WebUI 中导出/导入。

---

## 🗺️ 路线图

### v1.0（当前版本）
- [x] 基础框架搭建
- [x] Skill DSL 系统
- [x] AI 决策模块
- [x] 安全校验层
- [x] 故障容错
- [x] WebUI 控制面板
- [x] 15+ 内置 Skill

### v1.1（计划中）
- [ ] Skill 可视化编辑器（拖拽式）
- [ ] 更多内置 Skill（红石、附魔、酿造）
- [ ] WebUI 暗色主题
- [ ] 移动端适配

### v2.0（远期）
- [ ] 多 AI 协同（组队生存）
- [ ] 语音交互控制
- [ ] 地图探索与标记系统
- [ ] Skill 市场（社区分享）
- [ ] AI 自我进化机制

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- [pyCraft](https://github.com/ammaraskar/pyCraft) - Minecraft 协议库
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能 Web 框架
- [Vue.js](https://vuejs.org/) - 前端框架

---

<p align="center">
  <i>Made with ❤️ by Xingnuo · Flutter 小码娘</i>
</p>
