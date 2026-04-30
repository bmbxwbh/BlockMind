# 🧠 BlockMind — Intelligent Minecraft AI Companion System

> **Fabric Mod + AI-Driven + Memory System** · v3.0 · 2026-04-30

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![Fabric](https://img.shields.io/badge/Fabric-0.92+-yellow.svg)](https://fabricmc.net)
[![MC](https://img.shields.io/badge/Minecraft-1.20.x--1.21.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**In a nutshell:** Fabric Mod provides precise game interfaces + Python backend drives AI decision-making + memory system enables cross-session learning, achieving a 7×24 autonomous Minecraft AI companion.

🌐 [中文](README.md) | **English** | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | [Español](README-es.md) | [Français](README-fr.md) | [Bahasa Indonesia](README-id.md) | [Italiano](README-it.md) | [Português](README-pt.md) | [Русский](README-ru.md) | [ภาษาไทย](README-th.md) | [Türkçe](README-tr.md) | [Tiếng Việt](README-vi.md)
---

## 📖 Table of Contents

- [Highlights](#-highlights)
- [System Architecture](#-system-architecture)
- [Memory System](#-memory-system)
- [Smart Navigation](#-smart-navigation)
- [Dual-Agent Architecture](#-dual-agent-architecture)
- [Quick Start](#-quick-start)
- [One-Click Deployment](#-one-click-deployment)
- [Fabric Mod API](#-fabric-mod-api)
- [Skill DSL System](#-skill-dsl-system)
- [Security System](#-security-system)
- [WebUI Control Panel](#-webui-control-panel)
- [Deployment Guide](#-deployment-guide)
- [FAQ](#-faq)
- [Roadmap](#-roadmap)

---

## ✨ Highlights

### 🧠 Memory System — Cross-Session Learning (New in v3.0)

```
Traditional:   Forgets everything on every restart, repeats mistakes, burns tokens repeatedly
Memory-driven: Three-layer memory (spatial/path/strategy), persisted as JSON, reused across sessions
```

- **Spatial Memory**: Automatically detects and remembers building protection zones, danger areas, and resource points
- **Path Memory**: Caches successful paths, blacklists failed paths, tracks success rate statistics
- **Strategy Memory**: Successful operations automatically crystallize into reusable strategies — zero-token reuse
- **Building Protection**: Automatically avoids player-built structures during navigation — no more accidental destruction

### 🛤️ Smart Navigation — Memory-Driven Pathfinding (New in v3.0)

```
Traditional:   walk_to(x,y,z) → stuck on wall / blows through buildings
Smart:         Check memory → use cache → Baritone (exclude protection zones) → A* fallback
```

- **Cache First**: Previously traveled paths are reused directly — zero computation
- **Baritone Integration**: The community's strongest pathfinding engine — auto-dig, auto-bridge, auto-swim, lava avoidance
- **Building Protection Zone Injection**: Memorized buildings are automatically injected as Baritone exclusion zones
- **Auto-Learning**: Every navigation result is automatically recorded to the memory system

### 🤖 Dual-Agent Architecture — Chat and Action Isolation (New in v2.0)

```
Main Agent:     Handles chat, persistent context, intent recognition only (~50 tokens/call)
Action Agent:   Handles execution, stateless, fresh context each time (<1500 tokens/call)
```

- **Main Agent**: Maintains conversation context, recognizes `[TASK:xxx]` tags
- **Action Agent**: Stateless, disposable — avoids context explosion
- **Memory Injection**: Memory context (building protection zones, known paths, etc.) is automatically injected during AI decision-making

### 🔌 Fabric Mod Architecture — Precise and Reliable

- **Zero Protocol Parsing**: Directly calls game internal APIs
- **13 HTTP Endpoints** + WebSocket real-time events
- **Baritone Optional Integration**: Advanced pathfinding when available, basic linear movement as fallback

### 🛡️ Five-Level Security System

| Level | Name | Example | Policy |
|-------|------|---------|--------|
| 0 | Completely Safe | Move, jump | Auto-execute |
| 1 | Low Risk | Dig dirt, place torch | Auto-execute |
| 2 | Medium Risk | Mine ore, attack neutral mobs | Auto-execute |
| 3 | High Risk | Ignite TNT, place lava | Requires player authorization |
| 4 | Fatal Risk | Place command block | Disabled by default |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Minecraft Server                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            BlockMind Fabric Mod (Java)                 │  │
│  │                                                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │ State    │ │ Action   │ │ Event    │ │ Baritone │ │  │
│  │  │ Collector│ │ Executor │ │ Listener │ │ Engine   │ │  │
│  │  │ Blocks/  │ │ Move/Dig │ │ Chat/    │ │ (Optional│ │  │
│  │  │ Entities/│ │ Place/   │ │ Damage/  │ │  )       │ │  │
│  │  │ Inventory│ │ Attack   │ │ Block    │ │          │ │  │
│  │  │ /World   │ │          │ │ Changes  │ │          │ │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │  │
│  │       └─────────────┼────────────┼────────────┘       │  │
│  │               HTTP API :25580 + WebSocket              │  │
│  └─────────────────────────────┼──────────────────────────┘  │
└────────────────────────────────┼─────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────┐
│                  BlockMind Python Backend                     │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │               Dual-Agent Architecture                 │  │
│  │  ┌─────────────────┐  ┌────────────────────────────┐  │  │
│  │  │ Main Agent (Chat)│  │ Action Agent (Exec, Stateless│ │  │
│  │  │ Persistent ctx   │  │ Fresh context each time    │  │  │
│  │  │ Intent detection │  │ Skill match/gen/exec       │  │  │
│  │  └────────┬────────┘  └─────────────┬──────────────┘  │  │
│  └───────────┼─────────────────────────┼─────────────────┘  │
│              │                         │                     │
│  ┌───────────▼─────────────────────────▼─────────────────┐  │
│  │               🧠 Memory System (GameMemory)           │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │ Spatial  │ │ Path     │ │ Strategy │ │ Player   │ │  │
│  │  │ Memory   │ │ Memory   │ │ Memory   │ │ Memory   │ │  │
│  │  │ Building │ │ Success  │ │ Success  │ │ Home loc │ │  │
│  │  │ zones    │ │ paths    │ │ strategies│ │ Preferences│ │  │
│  │  │ Danger   │ │ Failed   │ │ Failed   │ │ Interact │ │  │
│  │  │ areas    │ │ blacklist│ │ records  │ │ logs     │ │  │
│  │  │ Resource │ │ Success  │ │ Context  │ │          │ │  │
│  │  │ nodes    │ │ rate     │ │ tags     │ │          │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │  │
│  │              Persisted JSON (data/memory/)             │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │ Injection                     │
│  ┌──────────┐ ┌──────────────▼──────┐ ┌──────────────────┐  │
│  │ Skill    │ │ Smart Navigator     │ │ AI Decision Layer│  │
│  │ Engine   │ │ Memory→Cache→       │ │ Memory context   │  │
│  │ DSL Parse│ │ Baritone→A*→        │ │ injection        │  │
│  │ Match &  │ │ Auto-learn          │ │ provider.py      │  │
│  │ Execute  │ │                     │ │                  │  │
│  └──────────┘ └─────────────────────┘ └──────────────────┘  │
│  ┌──────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │ Security │ │ Health       │ │ WebUI (Miuix Console)   │ │
│  │ Validator│ │ Monitor      │ │ Dark theme/Model config │ │
│  │ 5-level  │ │ 3-tier       │ │                         │ │
│  │ risk ctrl│ │ degradation  │ │                         │ │
│  └──────────┘ └──────────────┘ └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow Example

**Memory-Driven Smart Navigation:**
```
Player says "go home"
  → Main Agent identifies task [TASK:go home]
  → Action Agent matches go_home Skill
  → SmartNavigator queries memory:
      ✅ Home location: (65, 64, -120) from player memory
      ✅ Cached path: traveled 3 times, 100% success rate
      ✅ Building protection zone: 30-block radius around base, no breaking
      ✅ Danger zone: lava at (80, 12, -50)
  → Baritone navigation:
      GoalBlock(65, 64, -120)
      + exclusion_zones=[base protection zone]
      → Automatically reroutes, no buildings destroyed
  → On arrival: path cache success_count+1
  → Next "go home": directly follows cached path, zero token cost
```

---

## 🧠 Memory System

### Three-Layer Memory Architecture

| Layer | Storage Content | Persisted | Example |
|-------|----------------|-----------|---------|
| **Spatial Memory** | Building protection zones, danger areas, resource nodes, base | ✅ JSON | "Base range: (50-100, 60-80, -150--90)" |
| **Path Memory** | Successful path cache, failed path blacklist, success rate | ✅ JSON | "Home→Mine: via (70,64,-100) success rate 100%" |
| **Strategy Memory** | Success strategy crystallization, failure lessons, context tags | ✅ JSON | "Place torches before mining — most efficient" |
| **Player Memory** | Home location, preferred tools, interaction logs | ✅ JSON | "Steve's home is at (100,64,200)" |
| **World Memory** | Spawn point, safe points, important events | ✅ JSON | "Spawn (0,64,0), safe points list" |

### Automatic Building Protection

```python
# Register a building protection zone (AI cannot break blocks here)
memory.register_building("main_city", center=(100, 64, 200), radius=30)
# → Automatically injected into Baritone exclusion_zones during navigation
# → type: "no_break" + "no_place"
# → AI cannot break/place blocks within the protection zone

# Auto-detection (scans surroundings every 60 seconds)
navigator.auto_detect_and_memorize()
# → Detects consecutive building blocks → auto-registers as protection zone
# → Detects lava/fire → auto-registers as danger zone
# → Detects ore clusters → auto-registers as resource node
```

### Path Cache Mechanism

```python
# First navigation: AI plans + executes
result = await navigator.goto(100, 64, 200)
# → Caches path: success_count=1, success_rate=100%

# Second navigation: directly follows cache
result = await navigator.goto(100, 64, 200)
# → Cache hit, direct execution, zero computation

# Failed path: automatic learning
# → fail_count >= 3 → automatically blacklisted
# → Replans next time, avoids old route
```

### Automatic Strategy Crystallization

```python
# Automatically recorded after successful Action Agent execution
memory.record_strategy(
    task_type="mine",
    description="place torches before mining",
    action_sequence=[...],
    success=True,
    context_tags=["nighttime", "cave"],
)

# Automatically matches the best strategy for the same task type next time
best = memory.get_best_strategy("mine", context_tags=["nighttime"])
# → Returns the strategy with the highest success rate
```

### AI Memory Context Injection

```python
# Automatically injects memory on every AI decision
memory_context = memory.get_ai_context()
# Output:
# [Memory System]
# Base:
#   - Home: (50, 64, -100) (radius 30)
# Building Protection Zones (no breaking):
#   - Main City: (100, 64, 200) (radius 20)
# Danger Zones:
#   - Lava Lake: (80, 12, -50) (lava)
# Known Reliable Paths: 3
# Verified Strategies: 5
```

---

## 🛤️ Smart Navigation

### Navigation Flow

```
SmartNavigator.goto(x, y, z)
  │
  ├── 1. Safety Check
  │     └── Target inside a protection zone? → Warn but don't reject
  │
  ├── 2. Query Cached Path
  │     └── Reliable cache available? → Execute cached path directly
  │
  ├── 3. Gather Navigation Context
  │     ├── Exclusion zones (building protection)
  │     ├── Danger zones (lava, cliffs)
  │     └── Reliable path references
  │
  ├── 4. Baritone Pathfinding (preferred)
  │     ├── Inject exclusion_zones
  │     ├── Auto-dig / auto-bridge / auto-swim
  │     └── Fall cost / lava avoidance
  │
  ├── 5. A* Pathfinding (fallback)
  │     └── Basic grid A* + block passability check
  │
  └── 6. Record Result
        ├── Success → cache_path(success=True)
        └── Failure → cache_path(success=False) + possible blacklist
```

### Baritone Integration

| Feature | Baritone | Basic A* |
|---------|----------|----------|
| Pathfinding Algorithm | Improved A* + cost heuristics | Standard A* |
| Auto-Dig | ✅ Digs through obstacles automatically | ❌ |
| Auto-Bridge | ✅ Scaffold mode | ❌ |
| Swimming | ✅ | ❌ |
| Vertical Movement | ✅ Jump/ladder/vine | ⚠️ 1 block only |
| Lava Avoidance | ✅ Cost penalty | ❌ |
| Fall Cost | ✅ Factored into heuristic | ❌ |
| Exclusion Zones | ✅ `exclusionAreas` | ❌ |
| **Building Protection** | ✅ Injects `no_break` zones | ❌ |

### Exclusion Zone Types

| Type | Description | Source |
|------|-------------|--------|
| `no_break` | Block breaking prohibited | Building protection zones, base |
| `no_place` | Block placement prohibited | Building protection zones |
| `avoid` | Completely bypass | Danger zones (lava, etc.) |

---

## 🤖 Dual-Agent Architecture

### Why Dual Agents?

```
Single Agent Problem:
  Chat context + action context → token explosion (>4000/call)
  Action failures pollute chat → poor conversation experience
  Every action carries full chat history → wasteful

Dual Agent Solution:
  Main Agent: chat only, sliding window of 20 messages, ~50 tokens/call
  Action Agent: stateless, fresh context each time, <1500 tokens/call
```

### Flow

```
Player message
  → Main Agent chats (persistent context)
  → Detects [TASK:xxx] tag
  → Extracts task description
  → Action Agent executes (stateless):
      ├── Skill matching query
      ├── Memory context injection
      ├── L1/L2: Execute cached Skill
      ├── L3: AI fills template + executes
      └── L4: AI fully reasons + executes
  → Main Agent formats reply → Player
```

---
## 🚀 Quick Start

### Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.10+ |
| Java | 17+ |
| Minecraft | 1.19.4 - 1.21.4 |
| Fabric Loader | 0.15+ |

---

## 📦 One-Click Deployment

### Download

Download from [GitHub Releases](https://github.com/bmbxwbh/BlockMind/releases/latest):

| File | Description |
|------|-------------|
| `blockmind-mod-1.0.0.jar` | Fabric Mod (place in server mods/) |
| `Source code` (zip/tar) | Full source code |

### Linux / macOS One-Click Start

```bash
# Clone
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

# One-click start (auto-installs dependencies + MC server + BlockMind + WebUI)
chmod +x start.sh
./start.sh
```

> `start.sh` automatically: detects Python/Java → installs dependencies → scans for existing MC server → selects version and installs → starts everything

### Windows One-Click Start

```cmd
:: Clone (or download and extract zip)
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

:: One-click install
install.bat

:: One-click start (MC server + BlockMind + WebUI)
start_all.bat
```

> See [Windows Deployment Guide](docs/WINDOWS.md) for detailed steps.

### Docker Deployment

```bash
# Pull image
docker pull ghcr.io/bmbxwbh/blockmind:latest

# Download config template
wget https://raw.githubusercontent.com/bmbxwbh/BlockMind/main/config.example.yaml -O config.yaml
# Edit config.yaml with your AI model configuration

# Start
docker run -d \
  --name blockmind \
  -p 19951:19951 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v blockmind-data:/data \
  ghcr.io/bmbxwbh/blockmind:latest
```

Or use docker-compose:

```bash
git clone https://github.com/bmbxwbh/BlockMind.git && cd BlockMind
cp config.example.yaml config.yaml
# Edit config.yaml
docker compose up -d
```

```bash
# View logs
docker compose logs -f blockmind
# Stop
docker compose down
```

### Configuration

Edit `config.yaml`:

```yaml
ai:
  main_agent:
    provider: "openai"          # openai or anthropic
    api_key: "sk-your-key"
    model: "gpt-4o"             # Your model name
    base_url: ""                # Custom API endpoint (optional)

webui:
  enabled: true
  port: 19951
  auth:
    password: "your-password"   # WebUI login password
```

After starting, visit `http://localhost:19951` to access the control panel.

---

## 🔌 Fabric Mod API

### Status Queries

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/status` | GET | Player status |
| `/api/world` | GET | World status |
| `/api/inventory` | GET | Inventory info |
| `/api/entities?radius=32` | GET | Nearby entities |
| `/api/blocks?radius=16` | GET | Nearby blocks |

### Action Execution

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/move` | POST | Move to coordinates |
| `/api/dig` | POST | Dig block |
| `/api/place` | POST | Place block |
| `/api/attack` | POST | Attack entity |
| `/api/eat` | POST | Eat food |
| `/api/look` | POST | Look at coordinates |
| `/api/chat` | POST | Send chat message |

### Pathfinding

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/pathfind` | POST | Path navigation (Baritone/A*) |
| `/api/pathfind/stop` | POST | Stop navigation |
| `/api/pathfind/status` | GET | Navigation status |

### Event Streaming

The Mod pushes events via WebSocket:
- `player_damaged` — Player took damage
- `entity_attack` — Under attack
- `health_low` — Low health
- `inventory_full` — Inventory full
- `block_broken` — Block mining completed

---

## 📝 Skill DSL System

### Task Levels

| Level | Type | Example | Cache Strategy |
|-------|------|---------|----------------|
| L1 | Fixed Task | "Go home" | Direct execution |
| L2 | Parameterized Task | "Mine 10 diamonds" | Cached with parameters |
| L3 | Template Task | "Build a shelter" | Template matching |
| L4 | Dynamic Task | "Help me defeat the Ender Dragon" | AI reasoning |

### Skill YAML Example

```yaml
skill_id: mine_diamonds
name: "Mine Diamonds"
level: L2
parameters:
  count: {type: int, default: 10, min: 1, max: 64}
steps:
  - action: pathfind
    target: {y: -59}
    note: "Head to diamond level"
  - action: dig_loop
    block: diamond_ore
    count: ${count}
  - action: pathfind
    target: home
    note: "Return to base"
```

---

## 🛡️ Security System

| Layer | Mechanism | Description |
|-------|-----------|-------------|
| L1 | Risk Assessment | Every action scored 0-100 |
| L2 | Operation Authorization | High-risk actions require confirmation |
| L3 | Emergency Override | Player can interrupt AI at any time |
| L4 | Audit Log | All operations are traceable |
| L5 | Safe Zone Restriction | Limits breaking/placement range |

---

## 🖥️ WebUI Control Panel

After starting, visit `http://localhost:19951` for:

- 📊 Dashboard — Real-time status monitoring
- 🛠️ Skill Management — Edit YAML online
- 🧠 Memory System — View / Clear / Backup
- 🤖 Model Configuration — Hot-swap AI models
- 💬 Command Panel — Natural language commands
- 📋 Task Queue — View execution status
- 📝 Log Center — Real-time log stream

---

## ❓ FAQ

**Q: Is Baritone required?**
A: No. Baritone is an optional dependency — without it, the system automatically falls back to basic A* linear movement.

**Q: Where is memory data stored?**
A: In the `data/memory/` directory as 5 JSON files, preserved across sessions.

**Q: How does building protection work?**
A: Two ways: ① Manual registration ② Automatic detection (scans every 60 seconds).

**Q: Which AI providers are supported?**
A: OpenAI-compatible format (including DeepSeek/OpenRouter/MiMo, etc.) + Anthropic format.

**Q: How large is the Docker image?**
A: About 200MB, built with a python:3.11-slim multi-stage build.

---

## 🗺️ Roadmap

### v3.0 (Current) ✅
- [x] Three-layer memory system (spatial/path/strategy)
- [x] Smart navigation (memory-driven + Baritone integration)
- [x] Dual-agent architecture (chat/action isolation)
- [x] Automatic building protection zones
- [x] Miuix Console WebUI
- [x] Windows/Linux one-click deployment
- [x] Docker image + GHCR auto-publishing
- [x] GitHub Actions CI/CD

### v3.1 (Planned)
- [ ] Multimodal input (screenshot analysis)
- [ ] Skill marketplace (import/export)
- [ ] Multiplayer collaboration
- [ ] Voice interaction

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
