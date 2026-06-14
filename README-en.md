# 🧠 BlockMind

> **Fabric Mod + AI + Memory System** · Minecraft AI Companion

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![MC](https://img.shields.io/badge/Minecraft-1.20~26.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT--NC-purple.svg)](LICENSE)

Fabric Mod provides precise game interfaces + Python backend drives AI decisions + Memory system enables cross-session learning. **Supports both server and client modes** — works in singleplayer, LAN, or servers.

🌐 [中文](README.md) | **English** | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | [Español](README-es.md) | [Français](README-fr.md)

---

## Why BlockMind

### 1. Memory System — AI That Learns

Traditional AI companions forget everything on every restart. BlockMind has three-layer persistent memory:

- **Spatial Memory**: Automatically remembers building protection zones, danger areas, resource points
- **Path Memory**: Caches successful paths, blacklists failed paths, reuses directly next time
- **Strategy Memory**: Successful operations crystallize into reusable strategies — zero Token cost

AI navigation automatically avoids player buildings, never destroys your base.

### 2. Dual-Agent Architecture — Token-Efficient

```
Main Agent (~50 tokens/call): Chat + intent recognition only
Action Agent (<1500 tokens/call): Stateless, disposable execution
```

84% cost savings compared to single-agent approach (>4000 tokens/call).

### 3. Server + Client Dual Mode

| Mode | Install Location | Player | Use Case |
|------|-----------------|--------|----------|
| Server | Server `mods/` | FakePlayer (Bot) | 7×24 server idle |
| Client | Client `mods/` | Local player | Singleplayer / LAN |

### 4. Baritone Integration + Building Protection

AI uses Baritone for pathfinding (auto-dig/bridge/swim) but automatically routes around your building protection zones. Memorized buildings are injected into Baritone exclusion zones in real time.

### 5. Skill DSL + Marketplace

Define reusable AI skills (mining, farming, building) in YAML, share with community. AI-generated skills auto-save, zero Token cost on next execution.

---

## Quick Start

### Requirements

- Python 3.10+ · Java 17+ · Minecraft 1.20.0 ~ 26.1.2

### One-Click Start

```bash
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind
chmod +x start.sh && ./start.sh
```

### Windows

```cmd
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind
install.bat
start_all.bat
```

### Docker

```bash
docker pull ghcr.io/bmbxwbh/blockmind:latest
docker run -d --name blockmind -p 19951:19951 \
  -v ./config.yaml:/app/config.yaml:ro \
  ghcr.io/bmbxwbh/blockmind:latest
```

### Configuration

Edit `config.yaml`:

```yaml
ai:
  main_agent:
    provider: openai
    api_key: "sk-your-key"
    model: gpt-4o
webui:
  enabled: true
  port: 19951
```

After starting, visit `http://localhost:19951` for the control panel.

---

## Architecture

```
┌──────────────── Minecraft ────────────────┐
│  BlockMind Fabric Mod (Java)              │
│  State Collection · Action Execution      │
│  Event Listening                          │
│  HTTP API :25580 · WebSocket              │
└──────────────────┬────────────────────────┘
                   │
┌──────────────────▼────────────────────────┐
│  BlockMind Python Backend                 │
│  ┌──────────┐  ┌──────────────────────┐  │
│  │ Main     │  │ Action Agent         │  │
│  │ Agent    │  │ (Stateless)          │  │
│  │ Chat+ID  │  │ Skill match/gen/exec │  │
│  └─────┬────┘  └──────────┬───────────┘  │
│  ┌─────▼──────────────────▼───────────┐  │
│  │ Memory System · Smart Nav · Skill  │  │
│  └────────────────┬───────────────────┘  │
│  ┌────────────────▼───────────────────┐  │
│  │ WebUI Control Panel (MiuiX)        │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## WebUI Control Panel

`http://localhost:19951` — Lucide icons + MiuiX dark theme

| Feature | Description |
|---------|-------------|
| Dashboard | Real-time status, quick commands, event stream |
| Skill Management | Online YAML editor, one-click execution |
| Skill Marketplace | Community skills browse, install, import/export |
| Memory System | View / backup / cleanup / import/export |
| Model Config | Dual-agent model config, hot-swap |
| Security Settings | Risk levels, audit log |
| Task Queue | Execution status monitoring |
| Log Center | Real-time WebSocket log stream |

---

## Fabric Mod API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Player status |
| `/api/inventory` | GET | Inventory info |
| `/api/entities` | GET | Nearby entities |
| `/api/move` | POST | Move to coordinates |
| `/api/dig` | POST | Dig block |
| `/api/place` | POST | Place block |
| `/api/attack` | POST | Attack entity |
| `/api/chat` | POST | Send chat |

Full API docs: [Fabric Mod API](docs/MOD_BUILD.md).

---

## Version Support

| MC Version | Java | Status |
|------------|------|--------|
| 1.20.0 ~ 1.20.6 | 17~21 | ✅ |
| 1.21 ~ 1.21.4 | 21 | ✅ |
| 26.1 ~ 26.1.2 | 25 | ✅ Latest |

---

## FAQ

**Q: Is Baritone required?** No. Without it, the system falls back to basic A*.

**Q: Where is memory data stored?** In the `data/memory/` directory as 5 JSON files.

**Q: Which AI models are supported?** OpenAI-compatible format (DeepSeek/OpenRouter/MiMo) + Anthropic.

**Q: Can I use it in singleplayer?** Yes, just place the mod in your client `mods/` folder.

---

## License

MIT-NC — Non-commercial use only. See [LICENSE](LICENSE).
