# 🧠 BlockMind

> **Mod de Fabric + IA + Sistema de Memoria** · Compañero inteligente de Minecraft

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![MC](https://img.shields.io/badge/Minecraft-1.20~26.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT--NC-purple.svg)](LICENSE)

El Mod de Fabric proporciona interfaces precisas del juego + el backend Python impulsa las decisiones de IA + el sistema de memoria aprende entre sesiones. **Soporta tanto servidor como cliente**, usable en juegos individuales, LAN o servidores.

🌐 [中文](README.md) | [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | **Español** | [Français](README-fr.md)

---

## Por qué BlockMind

### 1. Sistema de memoria — La IA aprende

Los compañeros de IA tradicionales olvidan todo al reiniciar. BlockMind tiene tres capas de memoria persistente:

- **Memoria espacial**: Recuerda automáticamente zonas de construcción protegidas, áreas peligrosas y puntos de recursos
- **Memoria de rutas**: Almacena rutas exitosas, bloquea las fallidas, las reutiliza la próxima vez
- **Memoria de estrategias**: Las operaciones exitosas se consolidan como estrategias reutilizables, consumo cero de tokens

La IA navega evitando automáticamente las construcciones del jugador, nunca destruye la casa.

### 2. Arquitectura de doble Agente — Ahorro de tokens

```
Agente principal (~50 tokens/vez): Solo chat + identificación de intención
Agente de operaciones (<1500 tokens/vez): Ejecución sin estado, descartable
```

Comparado con un solo agente (>4000 tokens/vez), ahorra un 84% de costos.

### 3. Servidor + Cliente dual

| Modo | Ubicación | Jugador | Escenario |
|------|-----------|---------|-----------|
| Servidor | `mods/` del servidor | FakePlayer (Bot) | Servidor 7×24 |
| Cliente | `mods/` del cliente | Jugador local | Individual / LAN |

### 4. Baritone integrado + protección de construcciones

La IA usa Baritone para pathfinding (cavar/puentes/nado automáticos), pero evita automáticamente las zonas de construcción protegidas. Los edificios en memoria se inyectan como zonas de exclusión de Baritone en tiempo real.

### 5. Skill DSL + marketplace

Define habilidades reutilizables de IA en YAML (minería, agricultura, construcción), compartidas con la comunidad. Las habilidades generadas por IA se guardan automáticamente, ejecución sin tokens la próxima vez.

---

## Inicio rápido

### Requisitos

- Python 3.10+ · Java 17+ · Minecraft 1.20.0 ~ 26.1.2

### Un clic en Linux/macOS

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

### Configuración

Edita `config.yaml`:

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

Accede a `http://localhost:19951` para el panel de control.

---

## Arquitectura

```
┌──────────────── Minecraft ────────────────┐
│  BlockMind Fabric Mod (Java)              │
│  Recolección · Ejecución · Eventos        │
│  HTTP API :25580 · WebSocket              │
└──────────────────┬────────────────────────┘
                   │
┌──────────────────▼────────────────────────┐
│  Backend Python de BlockMind              │
│  ┌──────────┐  ┌──────────────────────┐  │
│  │Agente    │  │Agente de operaciones │  │
│  │principal │  │(sin estado)          │  │
│  │Chat+iden.│  │Match/ejecución Skills│  │
│  └─────┬────┘  └──────────┬───────────┘  │
│  ┌─────▼──────────────────▼───────────┐  │
│  │Memoria · Navegación · Skills       │  │
│  └────────────────┬───────────────────┘  │
│  ┌────────────────▼───────────────────┐  │
│  │WebUI (MiuiX)                      │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## Panel de control WebUI

`http://localhost:19951` — Iconos Lucide + tema oscuro MiuiX

| Función | Descripción |
|---------|-------------|
| Dashboard | Estado en tiempo real, accesos directos, flujo de eventos |
| Skills | Edición YAML en línea, ejecución con un clic |
| Marketplace | Explorar/instalar/importar/exportar skills comunitarias |
| Memoria | Ver/respaldar/limpiar/importar/exportar |
| Modelos | Configuración dual de agentes, cambio en caliente |
| Seguridad | Niveles de riesgo, registro de auditoría |
| Cola de tareas | Monitoreo de estado de ejecución |
| Logs | Flujo de logs en tiempo real vía WebSocket |

---

## API del Fabric Mod

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/status` | GET | Estado del jugador |
| `/api/inventory` | GET | Información del inventario |
| `/api/entities` | GET | Entidades cercanas |
| `/api/move` | POST | Mover a coordenadas |
| `/api/dig` | POST | Excavar bloque |
| `/api/place` | POST | Colocar bloque |
| `/api/attack` | POST | Atacar entidad |
| `/api/chat` | POST | Enviar mensaje de chat |

Documentación completa en [API del Fabric Mod](docs/MOD_BUILD.md).

---

## Versiones soportadas

| MC | Java | Estado |
|----|------|--------|
| 1.20.0 ~ 1.20.6 | 17~21 | ✅ |
| 1.21 ~ 1.21.4 | 21 | ✅ |
| 26.1 ~ 26.1.2 | 25 | ✅ Última |

---

## FAQ

**¿Es obligatorio instalar Baritone?** No, sin él se recurre a A* básico.

**¿Dónde se guardan los datos de memoria?** En `data/memory/`, 5 archivos JSON.

**¿Qué modelos de IA son compatibles?** Formato OpenAI (DeepSeek/OpenRouter/MiMo) + Anthropic.

**¿Se puede usar en individual?** Sí, coloca el Mod en `mods/` del cliente.

---

## Licencia

MIT-NC — Uso no comercial. Ver [LICENSE](LICENSE).
