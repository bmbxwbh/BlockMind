# BlockMind Fabric Mod — Build & Installation Guide

> BlockMind is a server-side Fabric Mod (Minecraft 1.20.4) that exposes an HTTP API on port **25580** for the Python AI backend to control the game.

---

## 1. Download Pre-built JAR from GitHub Actions

Every push to `main` automatically builds the mod JAR via GitHub Actions.

### Steps

1. Go to the repository: <https://github.com/bmbxwbh/BlockMind/actions>
2. Click the latest **"Build Mod & Docker Image"** workflow run.
3. Scroll to the bottom **Artifacts** section.
4. Download **`blockmind-mod`** — it contains the compiled JAR.
5. Extract the zip. You'll get a file like:
   ```
   blockmind-mod-1.0.0.jar
   ```

### Release builds

Tagged releases (`v*`) also publish the JAR on the [Releases](https://github.com/bmbxwbh/BlockMind/releases) page as a direct download.

---

## 2. Build Locally

### Prerequisites

| Requirement | Version |
|---|---|
| Java (JDK) | 17+ |
| Git | any recent version |

### Build steps

```bash
# Clone the repository
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind/mod

# Build the mod
./gradlew build --no-daemon

# The JAR will be at:
ls build/libs/blockmind-mod-*.jar
```

> **Windows:** use `gradlew.bat build --no-daemon` instead.

### Run in-game during development

```bash
# Start a local test server
./gradlew runServer
```

---

## 3. Install the Mod on a Minecraft Server

### Prerequisites

| Requirement | Version |
|---|---|
| Minecraft server | 1.20.x – 1.21.x |
| Fabric Loader | ≥ 0.15.0 |
| Fabric API | matching your MC version |

### Installation

1. **Install Fabric Loader** on your server if not already installed.
   Download from <https://fabricmc.net/use/server/> and follow the installer.

2. **Download Fabric API** JAR for your Minecraft version from
   <https://modrinth.com/mod/fabric-api> and place it in the `mods/` folder.

3. **Copy the BlockMind JAR** into the server's `mods/` folder:
   ```bash
   cp blockmind-mod-1.0.0.jar /path/to/server/mods/
   ```

4. **Start the server**:
   ```bash
   java -Xmx4G -jar fabric-server-launcher.jar nogui
   ```

5. Look for this in the console log to confirm it loaded:
   ```
   [BlockMind] ✅ BlockMind Mod ready! API on port 25580
   ```

6. Verify the API is running:
   ```bash
   curl http://localhost:25580/health
   # Expected: {"status":"ok","mod":"blockmind","pathfinder":"basic"}
   ```

### Optional: Baritone integration

If you also install [Baritone](https://github.com/cabaletta/baritone) in `mods/`, BlockMind will automatically use it for advanced pathfinding (`/api/navigate/goto`). Without Baritone, basic straight-line movement is used.

---

## 4. Configuration

The BlockMind mod itself requires **no configuration files** — it runs with sensible defaults. All configuration lives on the Python companion side (`config.yaml`).

### Key defaults

| Setting | Value | Notes |
|---|---|---|
| HTTP API port | `25580` | Hardcoded in the mod; Python side must match |
| API bind address | `0.0.0.0` | Listens on all interfaces |
| Thread pool | 4 threads | For HTTP request handling |

### Python-side configuration (`config.yaml`)

Copy the example config and edit it:

```bash
cp config.example.yaml config.yaml
```

The mod connection section in `config.yaml` must match:

```yaml
mod:
  host: "localhost"      # Server IP where the mod runs
  port: 25580            # Must match the mod's HTTP_PORT
  timeout: 10.0
  no_mod_mode: false     # Set true to skip mod connection (testing only)
```

### Environment variables (optional)

You can override some Python-side settings via env vars. See `config.example.yaml` for the full list of configurable options including:

- **Game connection** — server IP, port, username, auth mode
- **AI model** — provider, API key, model name
- **Safety** — risk levels, authorization timeouts
- **WebUI** — host, port, authentication
- **Logging** — level, file, rotation

---

## 5. Troubleshooting

### Mod doesn't load

| Symptom | Cause | Fix |
|---|---|---|
| `UnsupportedClassVersionError` | Wrong Java version | Use **Java 17+** |
| `Mod resolution encountered an error` | Missing Fabric API | Add Fabric API JAR to `mods/` |
| `Incompatible mod set!` | Fabric Loader too old | Update Fabric Loader to ≥ 0.15.0 |
| No BlockMind log lines at all | JAR not in `mods/` | Verify JAR is in the correct `mods/` folder |

### HTTP API not responding

```bash
# Test connectivity
curl -v http://localhost:25580/health
```

| Symptom | Cause | Fix |
|---|---|---|
| Connection refused | Server not started or wrong port | Wait for server to fully start; check logs |
| `Connection refused` from remote | Firewall | Open port 25580 in your firewall |
| Timeout | Server overloaded | Check server TPS; reduce load |

### Python companion can't connect to mod

| Symptom | Fix |
|---|---|
| `ConnectionRefusedError` | Ensure the Minecraft server is running and the mod loaded successfully |
| `no_mod_mode` is `true` | Set it to `false` in `config.yaml` |
| Wrong port | Verify `mod.port` in `config.yaml` matches the mod's port (25580) |
| WebSocket backoff keeps increasing | Check mod logs for errors; restart the server |

### Pathfinding issues

| Symptom | Fix |
|---|---|
| `/api/navigate/goto` returns `baritone not available` | Install Baritone mod, or use `/api/move` for basic movement |
| Bot gets stuck | Reduce move distance; check for obstacles at target coordinates |

### Performance

- The mod adds minimal overhead — it only starts an HTTP server and event listeners.
- If the server lags, check the Python companion's request rate. The mod uses a 4-thread pool; excessive concurrent requests may queue.
- For high-load scenarios, consider increasing the thread pool (requires source modification).

---

## API Endpoints Reference

Once installed, the mod exposes these endpoints on port 25580:

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/api/status` | GET | Player status (health, position, etc.) |
| `/api/world` | GET | World info (time, weather, dimension) |
| `/api/inventory` | GET | Player inventory contents |
| `/api/entities` | GET | Nearby entities (optional `?radius=32`) |
| `/api/blocks` | GET | Nearby blocks (optional `?radius=16&type=stone`) |
| `/api/move` | POST | Move the player |
| `/api/dig` | POST | Break a block |
| `/api/place` | POST | Place a block |
| `/api/attack` | POST | Attack an entity |
| `/api/eat` | POST | Eat food from inventory |
| `/api/look` | POST | Change look direction |
| `/api/chat` | POST | Send a chat message |
| `/api/navigate/goto` | POST | Navigate to coordinates (Baritone) |
| `/api/navigate/stop` | POST | Stop current navigation |
| `/api/navigate/status` | GET | Pathfinding engine status |

---

## Support

- **Issues:** <https://github.com/bmbxwbh/BlockMind/issues>
- **Logs:** Check `logs/blockmind.log` (mod side) and `logs/companion.log` (Python side)
