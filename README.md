# 🧠 BlockMind — 智能 Minecraft AI 玩伴系统

> **Fabric Mod + AI 驱动 + 记忆系统** · v3.0 · 2026-04-30

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![Fabric](https://img.shields.io/badge/Fabric-0.92+-yellow.svg)](https://fabricmc.net)
[![MC](https://img.shields.io/badge/Minecraft-1.20.x--1.21.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**一句话概括：** Fabric Mod 提供精准游戏接口 + Python 后端驱动 AI 决策 + 记忆系统跨会话学习，实现 7×24 小时自主生存的 Minecraft 智能玩伴。

---

## 📖 目录

- [项目特色](#-项目特色)
- [系统架构](#-系统架构)
- [记忆系统](#-记忆系统)
- [智能导航](#-智能导航)
- [双 Agent 架构](#-双-agent-架构)
- [快速开始](#-快速开始)
- [Fabric Mod API](#-fabric-mod-api)
- [Skill DSL 系统](#-skill-dsl-系统)
- [安全体系](#-安全体系)
- [WebUI 控制面板](#-webui-控制面板)
- [部署指南](#-部署指南)
- [FAQ](#-faq)
- [路线图](#-路线图)

---

## ✨ 项目特色

### 🧠 记忆系统 — 跨会话学习（v3.0 新增）

```
传统方式：  每次重启都忘光，重复犯错，重复消耗 Token
记忆方式：  空间/路径/策略三层记忆，持久化 JSON，跨会话复用
```

- **空间记忆**：自动检测并记住建筑保护区、危险区域、资源点
- **路径记忆**：缓存成功路径，黑名单失败路径，成功率统计
- **策略记忆**：成功操作自动沉淀为可复用策略，零 Token 复用
- **建筑保护**：导航时自动避开玩家建筑，再也不怕炸家

### 🛤️ 智能导航 — 记忆驱动的寻路（v3.0 新增）

```
传统方式：  walk_to(x,y,z) → 遇墙卡死 / 炸穿建筑
智能导航：  查记忆 → 走缓存 → Baritone(排除保护区) → A* 回退
```

- **缓存优先**：走过的路直接复用，零计算
- **Baritone 集成**：社区最强寻路引擎，自动挖路/搭桥/游泳/规避岩浆
- **建筑保护区注入**：记忆中的建筑自动注入为 Baritone 排除区域
- **自动学习**：每次导航结果自动记录到记忆系统

### 🤖 双 Agent 架构 — 聊天与操作隔离（v2.0 新增）

```
主 Agent：  负责聊天，持久上下文，只做意图识别（~50 Token/次）
操作 Agent：负责执行，无状态全新上下文（<1500 Token/次）
```

- **主 Agent**：保持对话上下文，识别 `[TASK:xxx]` 标签
- **操作 Agent**：无状态，用完即弃，避免上下文爆炸
- **记忆注入**：AI 决策时自动注入记忆上下文（建筑保护区、已知路径等）

### 🔌 Fabric Mod 架构 — 精准可靠

- **零协议解析**：直接调用游戏内部 API
- **13 个 HTTP 端点** + WebSocket 实时事件
- **Baritone 可选集成**：有则高级寻路，无则基础直线

### 🛡️ 五级安全体系

| 等级 | 名称 | 示例 | 策略 |
|------|------|------|------|
| 0 | 完全安全 | 移动、跳跃 | 自动执行 |
| 1 | 低风险 | 挖泥土、放火把 | 自动执行 |
| 2 | 中风险 | 挖矿石、攻击中立生物 | 自动执行 |
| 3 | 高风险 | 点燃TNT、放岩浆 | 需玩家授权 |
| 4 | 致命风险 | 放命令方块 | 默认禁止 |

---

## 🏗️ 系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                    Minecraft 服务器                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            BlockMind Fabric Mod (Java)                 │  │
│  │                                                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │状态采集器 │ │动作执行器 │ │事件监听器 │ │Baritone  │ │  │
│  │  │方块/实体/ │ │移动/挖掘/ │ │聊天/伤害/ │ │寻路引擎  │ │  │
│  │  │背包/世界  │ │放置/攻击  │ │方块变化   │ │(可选)    │ │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │  │
│  │       └─────────────┼────────────┼────────────┘       │  │
│  │               HTTP API :25580 + WebSocket              │  │
│  └─────────────────────────────┼──────────────────────────┘  │
└────────────────────────────────┼─────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────┐
│                  BlockMind Python 后端                        │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   双 Agent 架构                        │  │
│  │  ┌─────────────────┐  ┌────────────────────────────┐  │  │
│  │  │ 主 Agent (聊天)  │  │ 操作 Agent (执行,无状态)    │  │  │
│  │  │ 持久上下文       │  │ 每次全新上下文             │  │  │
│  │  │ 意图识别         │  │ Skill匹配/生成/执行        │  │  │
│  │  └────────┬────────┘  └─────────────┬──────────────┘  │  │
│  └───────────┼─────────────────────────┼─────────────────┘  │
│              │                         │                     │
│  ┌───────────▼─────────────────────────▼─────────────────┐  │
│  │               🧠 记忆系统 (GameMemory)                 │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │ 空间记忆  │ │ 路径记忆  │ │ 策略记忆  │ │ 玩家记忆  │ │  │
│  │  │ 建筑保护区│ │ 成功路径  │ │ 成功策略  │ │ 家位置   │ │  │
│  │  │ 危险区域  │ │ 失败黑名单│ │ 失败记录  │ │ 偏好习惯 │ │  │
│  │  │ 资源矿点  │ │ 成功率统计│ │ 上下文标签│ │ 交互记录 │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │  │
│  │              持久化 JSON (data/memory/)                 │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │ 注入                          │
│  ┌──────────┐ ┌──────────────▼──────┐ ┌──────────────────┐  │
│  │ Skill引擎│ │ 智能导航            │ │ AI 决策层         │  │
│  │ DSL解析  │ │ 记忆→缓存→Baritone  │ │ 记忆上下文注入    │  │
│  │ 匹配执行 │ │ →A*回退→自动学习    │ │ provider.py      │  │
│  └──────────┘ └─────────────────────┘ └──────────────────┘  │
│  ┌──────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │ 安全校验 │ │ 健康监控     │ │ WebUI (Miuix Console)   │ │
│  │ 五级风控 │ │ 三级降级     │ │ 暗色主题/模型配置       │ │
│  └──────────┘ └──────────────┘ └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### 数据流示例

**记忆驱动的智能导航：**
```
玩家说 "回家"
  → 主 Agent 识别任务 [TASK:回家]
  → 操作 Agent 匹配 go_home Skill
  → SmartNavigator 查询记忆：
      ✅ 家位置: (65, 64, -120) 来自玩家记忆
      ✅ 缓存路径: 走过3次, 成功率100%
      ✅ 建筑保护区: 基地周围30格禁止破坏
      ✅ 危险区域: (80,12,-50) 有岩浆
  → Baritone 导航：
      GoalBlock(65, 64, -120)
      + exclusion_zones=[基地保护区]
      → 自动绕路，不破坏任何建筑
  → 到达后：路径缓存 success_count+1
  → 下次回家：直接走缓存路径，零 Token 消耗
```

---

## 🧠 记忆系统

### 三层记忆架构

| 层 | 存储内容 | 持久化 | 示例 |
|---|---------|--------|------|
| **空间记忆** | 建筑保护区、危险区域、资源点、基地 | ✅ JSON | "基地范围: (50-100, 60-80, -150--90)" |
| **路径记忆** | 成功路径缓存、失败路径黑名单、成功率 | ✅ JSON | "家→矿洞: 经过(70,64,-100) 成功率100%" |
| **策略记忆** | 成功策略沉淀、失败教训、上下文标签 | ✅ JSON | "挖矿时先放火把再挖，效率最高" |
| **玩家记忆** | 家位置、偏好工具、交互记录 | ✅ JSON | "Steve 的家在 (100,64,200)" |
| **世界记忆** | 出生点、安全点、重要事件 | ✅ JSON | "出生点 (0,64,0), 安全点列表" |

### 自动建筑保护

```python
# 注册建筑保护区（禁止 AI 破坏）
memory.register_building("主城", center=(100, 64, 200), radius=30)
# → 导航时自动注入 Baritone exclusion_zones
# → type: "no_break" + "no_place"
# → AI 在保护区内无法破坏/放置方块

# 自动检测（每60秒扫描周围）
navigator.auto_detect_and_memorize()
# → 检测到连续建筑方块 → 自动注册为保护区
# → 检测到岩浆/火焰 → 自动注册为危险区
# → 检测到矿石聚集 → 自动注册为资源点
```

### 路径缓存机制

```python
# 第一次导航：AI 规划 + 执行
result = await navigator.goto(100, 64, 200)
# → 缓存路径: success_count=1, success_rate=100%

# 第二次导航：直接走缓存
result = await navigator.goto(100, 64, 200)
# → 命中缓存路径，直接执行，零计算

# 失败路径：自动学习
# → fail_count >= 3 → 自动加入黑名单
# → 下次重新规划，不走老路
```

### 策略自动沉淀

```python
# 操作 Agent 执行成功后自动记录
memory.record_strategy(
    task_type="mine",
    description="先放火把再挖矿",
    action_sequence=[...],
    success=True,
    context_tags=["nighttime", "cave"],
)

# 下次相同任务类型自动匹配最佳策略
best = memory.get_best_strategy("mine", context_tags=["nighttime"])
# → 返回成功率最高的策略
```

### AI 记忆上下文注入

```python
# 每次 AI 决策时自动注入记忆
memory_context = memory.get_ai_context()
# 输出：
# [记忆系统]
# 基地:
#   - 家: (50, 64, -100) (半径30)
# 建筑保护区（禁止破坏）:
#   - 主城: (100, 64, 200) (半径20)
# 危险区域:
#   - 岩浆湖: (80, 12, -50) (lava)
# 已知可靠路径: 3 条
# 已验证策略: 5 个
```

---

## 🛤️ 智能导航

### 导航流程

```
SmartNavigator.goto(x, y, z)
  │
  ├── 1. 安全检查
  │     └── 目标在保护区内？→ 警告但不拒绝
  │
  ├── 2. 查询缓存路径
  │     └── 有可靠缓存？→ 直接执行缓存路径
  │
  ├── 3. 获取导航上下文
  │     ├── 排除区域（建筑保护区）
  │     ├── 危险区域（岩浆、悬崖）
  │     └── 可靠路径参考
  │
  ├── 4. Baritone 寻路（优先）
  │     ├── 注入 exclusion_zones
  │     ├── 自动挖路 / 搭桥 / 游泳
  │     └── 摔落代价 / 岩浆规避
  │
  ├── 5. A* 寻路（回退）
  │     └── 基础网格 A* + 方块可通行判断
  │
  └── 6. 记录结果
        ├── 成功 → cache_path(success=True)
        └── 失败 → cache_path(success=False) + 可能黑名单
```

### Baritone 集成

| 特性 | Baritone | 基础 A* |
|------|----------|---------|
| 寻路算法 | 改进 A* + 代价启发 | 标准 A* |
| 挖路 | ✅ 自动挖穿障碍 | ❌ |
| 搭桥 | ✅ scaffold 模式 | ❌ |
| 游泳 | ✅ | ❌ |
| 垂直移动 | ✅ 跳跃/梯子/藤蔓 | ⚠️ 仅1格 |
| 岩浆规避 | ✅ 代价惩罚 | ❌ |
| 摔落代价 | ✅ 计入启发函数 | ❌ |
| 排除区域 | ✅ `exclusionAreas` | ❌ |
| **建筑保护** | ✅ 注入 `no_break` 区域 | ❌ |

### 排除区域类型

| 类型 | 说明 | 来源 |
|------|------|------|
| `no_break` | 禁止破坏方块 | 建筑保护区、基地 |
| `no_place` | 禁止放置方块 | 建筑保护区 |
| `avoid` | 完全绕开 | 危险区域（岩浆等） |

---

## 🤖 双 Agent 架构

### 为什么需要双 Agent？

```
单 Agent 问题：
  聊天上下文 + 操作上下文 → Token 爆炸（>4000/次）
  操作失败污染聊天 → 对话体验差
  每次操作都要带完整聊天历史 → 浪费

双 Agent 方案：
  主 Agent：只聊天，滑动窗口 20 条，~50 Token/次
  操作 Agent：无状态，全新上下文，<1500 Token/次
```

### 流程

```
玩家消息
  → 主 Agent 聊天（持久上下文）
  → 识别到 [TASK:xxx] 标签
  → 提取任务描述
  → 操作 Agent 执行（无状态）：
      ├── 查询 Skill 匹配
      ├── 注入记忆上下文
      ├── L1/L2: 执行缓存 Skill
      ├── L3: AI 填充模板 + 执行
      └── L4: AI 完全推理 + 执行
  → 主 Agent 格式化回复 → 玩家
```

---

## 🚀 快速开始

### 环境要求

| 组件 | 要求 |
|------|------|
| Python | 3.9+ |
| Java | 17+ |
| Minecraft | 1.20.x - 1.21.x |
| Fabric Loader | 0.92+ |

### 安装

```bash
# 克隆
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

# Python 环境
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 编译 Mod
cd mod && ./gradlew build
cp build/libs/blockmind-mod-1.0.0.jar /path/to/server/mods/

# 配置
cd .. && cp config/config.example.yaml config.yaml

# 启动
python -m src.main
```

### 配置示例

```yaml
game:
  server_ip: "localhost"
  server_port: 25565
  username: "BlockMind"

ai:
  main_agent:
    provider: "openai"
    model: "gpt-4o"
    temperature: 0.7
  operation_agent:
    provider: "openai"
    model: "gpt-4o"
    temperature: 0.3

memory:
  enabled: true
  storage_path: data/memory
  auto_detect_zones: true
  protect_buildings: true

navigation:
  prefer_baritone: true
  fallback_to_basic: true
  allow_break_default: false
```

---

## 🔌 Fabric Mod API

### 状态查询

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/status` | GET | 玩家状态 |
| `/api/world` | GET | 世界状态 |
| `/api/inventory` | GET | 背包信息 |
| `/api/entities?radius=32` | GET | 附近实体 |
| `/api/blocks?radius=16` | GET | 附近方块 |

### 动作执行

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/move` | POST | 移动到坐标 |
| `/api/dig` | POST | 挖掘方块 |
| `/api/place` | POST | 放置方块 |
| `/api/attack` | POST | 攻击实体 |
| `/api/eat` | POST | 进食 |
| `/api/look` | POST | 看向坐标 |
| `/api/chat` | POST | 发送聊天 |

### 智能导航（v3.0 新增）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/navigate/goto` | POST | 智能导航（带排除区域） |
| `/api/navigate/stop` | POST | 停止导航 |
| `/api/navigate/status` | GET | 寻路引擎状态 |

```json
// POST /api/navigate/goto
{
  "x": 100, "y": 64, "z": 200,
  "exclusion_zones": [
    {"center": [100, 64, 200], "radius": 30, "type": "no_break", "name": "基地"}
  ],
  "allow_break": false,
  "allow_place": false
}
```

---

## 📝 Skill DSL 系统

### 语法规范

```yaml
skill_id: string      # 唯一标识
name: string          # 显示名称
tags: list[string]    # 检索标签
priority: int         # 1=最高, 5=最低
task_level: L1|L2|L3|L4  # 任务分级
when:                 # 触发条件
  all: [expression]
do: [statement]       # 执行逻辑
until:                # 结束条件
  any: [expression]
```

### 智能导航动作（v3.0 新增）

```yaml
# 所有导航类 Skill 使用 smart_navigate 替代 walk_to
do:
  - action: smart_navigate
    args:
      target: "home"           # 从记忆获取目标位置
      allow_break: false       # 不破坏建筑
      allow_place: false       # 不放置方块
      use_cache: true          # 优先走缓存路径
```

### 内置 Skill

| 分类 | Skill | 说明 |
|------|-------|------|
| 🏠 导航 | `go_home` | 回家（记忆驱动） |
| 🛡️ 生存 | `sleep` | 睡觉（记忆床位置） |
| | `eat_food` | 进食 |
| 🪓 采集 | `chop_tree` | 砍树（避开保护区） |
| | `mine_ore` | 挖矿（避开危险区） |
| | `fish` | 钓鱼（记忆水域） |
| | `collect` | 采集 |
| 🌾 农业 | `plant_wheat` | 种田（记忆农场） |
| 📦 存储 | `deposit_items` | 存放物品 |
| | `organize_chest` | 整理箱子 |
| ⚔️ 战斗 | `kill_mob` | 杀怪（动态导航） |

---

## 🛡️ 安全体系

### 玩家远程指令

| 指令 | 功能 |
|------|------|
| `!stop` | 终止所有任务 |
| `!status` | 查看状态（含记忆统计） |
| `!memory` | 查看记忆系统详情 |
| `!safe` | 前往最近安全点 |
| `!help` | 帮助信息 |

---

## 🖥️ WebUI 控制面板

基于 [Miuix Console](https://github.com/bmbxwbh/miuix-console) 设计系统：

| 特性 | 说明 |
|------|------|
| 🎨 MiSans 字体 | 小米官方字体 |
| 🌙 深色/浅色 | 主题切换 |
| 📱 响应式 | 桌面侧边栏 + 手机底部导航 |
| 📊 数据表格 | mx-table 手机端卡片式 |
| 💬 轻提示 | MxToast 涟漪效果 |

| 页面 | 功能 |
|------|------|
| 📊 仪表盘 | 状态卡片、任务进度 |
| 🛠️ Skill 管理 | 浏览/编辑/测试 |
| ⚙️ 模型配置 | 双 Agent 独立配置 |
| 🛡️ 安全设置 | 风险等级、授权策略 |
| 📋 日志中心 | 日志查询、统计 |

---

## 🚀 部署

### Systemd

```bash
sudo bash scripts/deploy.sh
sudo systemctl start blockmind
```

### Docker

```bash
docker-compose up -d
```

### CI/CD

GitHub Actions 自动化：
- `build-mod` → Gradle 构建 JAR
- `test-python` → pytest 59 个测试
- `build-docker` → 推送 GHCR
- `release` → tag 触发自动发布

---

## ❓ FAQ

**Q: 必须装 Baritone 吗？**
A: 不必须。Baritone 是 `compileOnly` 可选依赖。没有时自动回退到基础 A* 直线移动。

**Q: 记忆数据存在哪？**
A: `data/memory/` 目录下，5 个 JSON 文件（zones/paths/strategies/players/world），跨会话保留。

**Q: 建筑保护怎么生效？**
A: 两种方式：① 手动 `register_building()` 注册 ② 自动检测（每60秒扫描周围建筑方块）。注册后自动注入 Baritone 排除区域。

**Q: 支持哪些 AI 提供商？**
A: OpenAI 格式（含 DeepSeek/OpenRouter/MiMo/本地模型）+ Anthropic 格式。双 Agent 可独立配置不同模型。

---

## 🗺️ 路线图

### v3.0（当前）✅
- [x] 三层记忆系统（空间/路径/策略）
- [x] 智能导航（记忆驱动 + Baritone 集成）
- [x] 双 Agent 架构（聊天/操作隔离）
- [x] 建筑保护区自动保护
- [x] Miuix Console WebUI

### v3.1（计划中）
- [ ] 记忆系统的 WebUI 可视化管理
- [ ] 路径记忆的热力图展示
- [ ] 多玩家记忆隔离
- [ ] MCP Server 接口
- [ ] 多机器人协同

---

## 📄 许可证

MIT License

---

<p align="center">
  <i>🧠 BlockMind — Every block has a mind.</i>
</p>
