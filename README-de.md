# 🧠 BlockMind

> **Fabric Mod + AI + Gedächtnissystem** · Minecraft AI-Kompanion

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![MC](https://img.shields.io/badge/Minecraft-1.20~26.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT--NC-purple.svg)](LICENSE)

Fabric Mod liefert präzise Spiel-Schnittstellen + Python-Backend steuert KI-Entscheidungen + Gedächtnissystem ermöglicht sitzungsübergreifendes Lernen. **Unterstützt Server- und Client-Modus** — funktioniert im Einzelspieler, LAN oder auf Servern.

🌐 [中文](README.md) | [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | **Deutsch** | [Español](README-es.md) | [Français](README-fr.md)

---

## Warum BlockMind

### 1. Gedächtnissystem — KI, die lernt

Traditionelle KI-Kompanons vergessen bei jedem Neustart alles. BlockMind hat ein dreischichtiges persistentes Gedächtnis:

- **Raumgedächtnis**: Merkt sich automatisch geschützte Bauwerke, Gefahrenzonen, Ressourcenpunkte
- **Pfadgedächtnis**: Cacht erfolgreiche Pfade, blacklistet fehlgeschlagene, wird nächstes Mal direkt wiederverwendet
- **Strategiegedächtnis**: Erfolgreiche Aktionen werden automatisch zu wiederverwendbaren Strategien kristallisiert — null Token-Verbrauch

Navigation umgeht automatisch Spielerbauten, zerstört nie die Basis.

### 2. Dual-Agent-Architektur — Token-effizient

```
Haupt-Agent (~50 Token/Aufruf): Nur Chat + Absichtserkennung
Ausführungs-Agent (<1500 Token/Aufruf): Zustandslos, wegwerfbar
```

84% Kostenersparnis gegenüber Single-Agent-Ansatz (>4000 Token/Aufruf).

### 3. Server + Client Dual-Modus

| Modus | Installationsort | Spieler | Szenario |
|-------|-----------------|---------|----------|
| Server | Server `mods/` | FakePlayer (Bot) | Server 7×24 im Leerlauf |
| Client | Client `mods/` | Lokaler Spieler | Einzelspieler / LAN |

### 4. Baritone-Integration + Bauschutz

KI nutzt Baritone zur Wegfindung (automatisch graben/Brücken bauen/schwimmen), umgeht aber automatisch deine Bauschutz-Zonen. Gemerkte Gebäude werden in Echtzeit in Baritone-Ausschlusszonen injiziert.

### 5. Skill DSL + Marktplatz

Definiere wiederverwendbare KI-Skills (Abbau, Landwirtschaft, Bau) in YAML, teile mit der Community. KI-generierte Skills werden automatisch gespeichert, nächstes Mal null Token-Verbrauch.

---

## Schnellstart

### Voraussetzungen

- Python 3.10+ · Java 17+ · Minecraft 1.20.0 ~ 26.1.2

### Ein-Klick-Start

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

### Konfiguration

`config.yaml` bearbeiten:

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

Nach dem Start unter `http://localhost:19951` die Konsole öffnen.

---

## Architektur

```
┌──────────────── Minecraft ────────────────┐
│  BlockMind Fabric Mod (Java)              │
│  Zustandserfassung · Aktionsexekution     │
│  Event-Listener                           │
│  HTTP API :25580 · WebSocket              │
└──────────────────┬────────────────────────┘
                   │
┌──────────────────▼────────────────────────┐
│  BlockMind Python-Backend                  │
│  ┌──────────┐  ┌──────────────────────┐  │
│  │ Haupt-   │  │ Ausführungs-Agent    │  │
│  │ Agent    │  │ (zustandslos)        │  │
│  │ Chat+    │  │ Skill-Matching/      │  │
│  │ Erkennung│  │ Generierung/Ausführung│ │
│  └─────┬────┘  └──────────┬───────────┘  │
│  ┌─────▼──────────────────▼───────────┐  │
│  │ Gedächtnissystem · Smarte Nav ·    │  │
│  │ Skill-Engine                       │  │
│  └────────────────┬───────────────────┘  │
│  ┌────────────────▼───────────────────┐  │
│  │ WebUI-Konsole (MiuiX)              │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## WebUI-Konsole

`http://localhost:19951` — Lucide-Symbole + MiuiX-Dunkles-Thema

| Funktion | Beschreibung |
|----------|-------------|
| Dashboard | Echtzeit-Status, Schnellbefehle, Event-Stream |
| Skill-Verwaltung | Online YAML bearbeiten, Ein-Klick-Ausführung |
| Skill-Marktplatz | Community-Skills durchsuchen, installieren, Import/Export |
| Gedächtnissystem | Ansehen / Sichern / Bereinigen / Import/Export |
| Modell-Konfiguration | Dual-Agent Modell-Konfiguration, Hot-Swap |
| Sicherheitseinstellungen | Risikostufen, Audit-Protokoll |
| Aufgabenwarteschlange | Ausführungsstatus-Überwachung |
| Protokollzentrale | Echtzeit WebSocket-Log-Stream |

---

## Fabric Mod API

| Endpunkt | Methode | Beschreibung |
|----------|---------|-------------|
| `/api/status` | GET | Spielerstatus |
| `/api/inventory` | GET | Inventarinformationen |
| `/api/entities` | GET | Nahe Entitäten |
| `/api/move` | POST | Zu Koordinaten bewegen |
| `/api/dig` | POST | Block abbauen |
| `/api/place` | POST | Block platzieren |
| `/api/attack` | POST | Entität angreifen |
| `/api/chat` | POST | Chat-Nachricht senden |

Vollständige API-Dokumentation: [Fabric Mod API](docs/MOD_BUILD.md).

---

## Versionsunterstützung

| MC-Version | Java | Status |
|------------|------|--------|
| 1.20.0 ~ 1.20.6 | 17~21 | ✅ |
| 1.21 ~ 1.21.4 | 21 | ✅ |
| 26.1 ~ 26.1.2 | 25 | ✅ Neueste |

---

## FAQ

**F: Muss Baritone installiert sein?** Nein. Ohne Baritone wird auf einfaches A* zurückgegriffen.

**F: Wo werden die Gedächtnisdaten gespeichert?** Im Verzeichnis `data/memory/` als 5 JSON-Dateien.

**F: Welche KI-Modelle werden unterstützt?** OpenAI-kompatibles Format (DeepSeek/OpenRouter/MiMo) + Anthropic.

**F: Kann ich es im Einzelspieler nutzen?** Ja, einfach den Mod in den Client-Ordner `mods/` legen.

---

## Lizenz

MIT-NC — Keine kommerzielle Nutzung. Siehe [LICENSE](LICENSE).
