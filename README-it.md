# 🧠 BlockMind

> **Mod Fabric + AI + Sistema di Memoria** · Compagno di gioco intelligente Minecraft

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![MC](https://img.shields.io/badge/Minecraft-1.20~26.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT--NC-purple.svg)](LICENSE)

Il Mod Fabric fornisce interfacce di gioco precise + il backend Python guida le decisioni AI + il sistema di memoria impara tra le sessioni. **Supporta server e client**, utilizzabile in singolo, LAN o server.

🌐 [中文](README.md) | [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | [Español](README-es.md) | [Français](README-fr.md)

---

## Perché BlockMind

### 1. Sistema di memoria — L'AI impara

I compagni AI tradizionali dimenticano tutto al riavvio. BlockMind ha tre livelli di memoria persistente:

- **Memoria spaziale**: Ricorda automaticamente le zone di costruzione protette, le aree pericolose e i punti risorsa
- **Memoria dei percorsi**: Memorizza i percorsi riusciti, mette in lista nera quelli falliti, riutilizzo successivo
- **Memoria strategica**: Le operazioni riuscite si consolidano in strategie riutilizzabili, consumo token zero

L'AI naviga evitando automaticamente le costruzioni del giocatore, non distrugge mai la casa.

### 2. Architettura a doppio Agente — Risparmio token

```
Agente principale (~50 token/chiamata): Solo chat + identificazione intenzione
Agente operativo (<1500 token/chiamata): Esecuzione senza stato, monouso
```

Rispetto a un singolo agente (>4000 token/chiamata), risparmio del 84% dei costi.

### 3. Server + Client dual

| Modalità | Posizione | Giocatore | Scenario |
|----------|-----------|-----------|----------|
| Server | `mods/` del server | FakePlayer (Bot) | Server 7×24 |
| Client | `mods/` del client | Giocatore locale | Singolo / LAN |

### 4. Baritone integrato + protezione costruzioni

L'AI usa Baritone per il pathfinding (scavo/ponti/nuoto automatici), ma evita automaticamente le zone di costruzione protette. Gli edifici in memoria vengono iniettati come zone di esclusione Baritone in tempo reale.

### 5. Skill DSL + marketplace

Definisci skill AI riutilizzabili in YAML (minagria, agricoltura, costruzione), condivise con la community. Le skill generate dall'AI vengono salvate automaticamente, esecuzione senza token la prossima volta.

---

## Guida rapida

### Requisiti

- Python 3.10+ · Java 17+ · Minecraft 1.20.0 ~ 26.1.2

### Un clic Linux/macOS

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

### Configurazione

Modifica `config.yaml`:

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

Accedi a `http://localhost:19951` per il pannello di controllo.

---

## Architettura

```
┌──────────────── Minecraft ────────────────┐
│  BlockMind Fabric Mod (Java)              │
│  Raccolta · Esecuzione · Eventi           │
│  HTTP API :25580 · WebSocket              │
└──────────────────┬────────────────────────┘
                   │
┌──────────────────▼────────────────────────┐
│  Backend Python BlockMind                 │
│  ┌──────────┐  ┌──────────────────────┐  │
│  │Agente    │  │Agente operativo      │  │
│  │principale│  │(senza stato)         │  │
│  │Chat+iden.│  │Match/esec. Skills    │  │
│  └─────┬────┘  └──────────┬───────────┘  │
│  ┌─────▼──────────────────▼───────────┐  │
│  │Memoria · Navigazione · Skills      │  │
│  └────────────────┬───────────────────┘  │
│  ┌────────────────▼───────────────────┐  │
│  │WebUI (MiuiX)                      │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## Pannello di controllo WebUI

`http://localhost:19951` — Icone Lucide + tema scuro MiuiX

| Funzione | Descrizione |
|----------|-------------|
| Dashboard | Stato in tempo reale, scorciatoie, flusso eventi |
| Skills | Modifica YAML在线, esecuzione con un clic |
| Marketplace | Esplora/installa/importa/esporta skill community |
| Memoria | Visualizza/backup/elimina/importa/esporta |
| Modelli | Configurazione dual agent, switching a caldo |
| Sicurezza | Livelli di rischio, log di audit |
| Coda task | Monitoraggio stato esecuzione |
| Log | Flusso log in tempo reale via WebSocket |

---

## API del Fabric Mod

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/api/status` | GET | Stato giocatore |
| `/api/inventory` | GET | Info inventario |
| `/api/entities` | GET | Entità vicine |
| `/api/move` | POST | Muovi a coordinate |
| `/api/dig` | POST | Scava blocco |
| `/api/place` | POST | Posiziona blocco |
| `/api/attack` | POST | Attacca entità |
| `/api/chat` | POST | Invia messaggio chat |

Documentazione completa in [API Fabric Mod](docs/MOD_BUILD.md).

---

## Versioni supportate

| MC | Java | Stato |
|----|------|-------|
| 1.20.0 ~ 1.20.6 | 17~21 | ✅ |
| 1.21 ~ 1.21.4 | 21 | ✅ |
| 26.1 ~ 26.1.2 | 25 | ✅ Ultima |

---

## FAQ

**Baritone è obbligatorio?** No, senza di esso si ricorre ad A* base.

**Dove vengono salvati i dati della memoria?** In `data/memory/`, 5 file JSON.

**Quali modelli AI sono supportati?** Formato OpenAI (DeepSeek/OpenRouter/MiMo) + Anthropic.

**Utilizzabile in singolo?** Sì, inserite il Mod in `mods/` del client.

---

## Licenza

MIT-NC — Uso non commerciale. Vedere [LICENSE](LICENSE).
