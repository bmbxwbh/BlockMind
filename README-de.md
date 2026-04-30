# 🧠 BlockMind — Intelligenter Minecraft AI-Spieler-Kompanion

> **Fabric Mod + KI-gesteuert + Gedächtnissystem** · v3.0 · 2026-04-30

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![Fabric](https://img.shields.io/badge/Fabric-0.92+-yellow.svg)](https://fabricmc.net)
[![MC](https://img.shields.io/badge/Minecraft-1.20.x--1.21.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**Kurzbeschreibung:** Fabric Mod liefert präzise Spiel-Schnittstellen + Python-Backend steuert KI-Entscheidungen + Gedächtnissystem lernt sitzungsübergreifend — ein 7×24 Stunden autonom überlebender Minecraft-KI-Kompanion.

🌐 [中文](README.md) | [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | **Deutsch** | [Español](README-es.md) | [Français](README-fr.md) | [Bahasa Indonesia](README-id.md) | [Italiano](README-it.md) | [Português](README-pt.md) | [Русский](README-ru.md) | [ภาษาไทย](README-th.md) | [Türkçe](README-tr.md) | [Tiếng Việt](README-vi.md)
---

## 📖 Inhaltsverzeichnis

- [Projekthighlights](#-projekthighlights)
- [Systemarchitektur](#-systemarchitektur)
- [Gedächtnissystem](#-gedächtnissystem)
- [Intelligente Navigation](#-intelligente-navigation)
- [Dual-Agent-Architektur](#-dual-agent-architektur)
- [Schnellstart](#-schnellstart)
- [Ein-Klick-Bereitstellung](#-ein-klick-bereitstellung)
- [Fabric Mod API](#-fabric-mod-api)
- [Skill-DSL-System](#-skill-dsl-system)
- [Sicherheitssystem](#-sicherheitssystem)
- [WebUI-Konsole](#-webui-konsole)
- [Bereitstellungshandbuch](#-bereitstellungshandbuch)
- [FAQ](#-faq)
- [Roadmap](#-roadmap)

---

## ✨ Projekthighlights

### 🧠 Gedächtnissystem — Sitzungsübergreifendes Lernen (v3.0, neu)

```
Traditionell:   Bei jedem Neustart alles vergessen, wiederholte Fehler, wiederholter Token-Verbrauch
Mit Gedächtnis: Drei Ebenen (Raum/Pfad/Strategie), persistente JSON, sitzungsübergreifend wiederverwendbar
```

- **Raumgedächtnis**: Erkennt und merkt sich automatisch geschützte Bauwerke, Gefahrenzonen, Ressourcenpunkte
- **Pfadgedächtnis**: Erfolgreiche Pfade werden zwischengespeichert, fehlgeschlagene auf die Blacklist gesetzt, Erfolgsquoten-Statistik
- **Strategiegedächtnis**: Erfolgreiche Aktionen werden automatisch als wiederverwendbare Strategien gespeichert — Null Token-Aufwand
- **Bauschutz**: Umgeht beim Navigieren automatisch Spielerbauten — kein versehentliches Zerstören mehr

### 🛤️ Intelligente Navigation — Gedächtnisgesteuerte Wegfindung (v3.0, neu)

```
Traditionell:   walk_to(x,y,z) → steckt in der Wand fest / sprengt Gebäude
Intelligent:    Gedächtnis prüfen → Cache nutzen → Baritone (Schutzzonen ausschließen) → A* Fallback
```

- **Cache zuerst**: Bereits gelaufene Wege werden direkt wiederverwendet, null Berechnung
- **Baritone-Integration**: Die stärkste Wegfindungs-Engine der Community — automatisch graben, Brücken bauen, schwimmen, Lava meiden
- **Bauschutz-Zonen**: Aus dem Gedächtnis bekannte Gebäude werden automatisch als Baritone-Ausschlusszonen injiziert
- **Automatisches Lernen**: Jedes Navigationsergebnis wird automatisch im Gedächtnissystem protokolliert

### 🤖 Dual-Agent-Architektur — Chat und Ausführung getrennt (v2.0, neu)

```
Haupt-Agent:    Übernimmt den Chat, persistenter Kontext, nur Absichtserkennung (~50 Token/Aufruf)
Ausführungs-Agent: Führt Aktionen aus, zustandslos, frischer Kontext (<1500 Token/Aufruf)
```

- **Haupt-Agent**: Behält den Dialogkontext, erkennt `[TASK:xxx]`-Tags
- **Ausführungs-Agent**: Zustandslos, nach Gebrauch verworfen — verhindert Kontext-Explosion
- **Gedächtnis-Injection**: Bei KI-Entscheidungen wird automatisch Gedächtnis-Kontext injiziert (geschützte Bauwerke, bekannte Pfade etc.)

### 🔌 Fabric Mod Architektur — Präzise und zuverlässig

- **Null Protokoll-Analyse**: Direkter Aufruf der internen Spiel-API
- **13 HTTP-Endpunkte** + WebSocket-Echtzeit-Events
- **Baritone optional**: Wenn vorhanden, erweiterte Wegfindung; sonst einfache Geradeaus-Navigation

### 🛡️ Fünfstufiges Sicherheitssystem

| Stufe | Name | Beispiel | Strategie |
|-------|------|----------|-----------|
| 0 | Völlig sicher | Bewegen, Springen | Automatisch ausführen |
| 1 | Geringes Risiko | Erde abbauen, Fackel setzen | Automatisch ausführen |
| 2 | Mittleres Risiko | Erz abbauen, neutrale Kreaturen angreifen | Automatisch ausführen |
| 3 | Hohes Risiko | TNT zünden, Lava platzieren | Spielererlaubnis erforderlich |
| 4 | Tödliches Risiko | Befehlsblock platzieren | Standardmäßig verboten |

---

## 🏗️ Systemarchitektur

```
┌──────────────────────────────────────────────────────────────┐
│                    Minecraft-Server                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            BlockMind Fabric Mod (Java)                 │  │
│  │                                                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Zustands- │ │Aktions-  │ │Event-    │ │Baritone  │ │  │
│  │  │Erfasser  │ │Ausführer │ │Listener  │ │Wegfindung│ │  │
│  │  │Blöcke/   │ │Bewegen/  │ │Chat/     │ │Engine    │ │  │
│  │  │Entitäten/│ │Graben/   │ │Schaden/  │ │(optional)│ │  │
│  │  │Inventar/ │ │Platzieren│ │Block-    │ │          │ │  │
│  │  │Welt      │ │Angreifen │ │änderungen│ │          │ │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │  │
│  │       └─────────────┼────────────┼────────────┘       │  │
│  │               HTTP API :25580 + WebSocket              │  │
│  └─────────────────────────────┼──────────────────────────┘  │
└────────────────────────────────┼─────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────┐
│                  BlockMind Python-Backend                     │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │               Dual-Agent-Architektur                   │  │
│  │  ┌─────────────────┐  ┌────────────────────────────┐  │  │
│  │  │ Haupt-Agent     │  │ Ausführungs-Agent          │  │  │
│  │  │ (Chat,          │  │ (zustandslos,              │  │  │
│  │  │  persistenter   │  │ frischer Kontext           │  │  │
│  │  │  Kontext)       │  │ frischer Kontext)          │  │  │
│  │  │ Absichts-       │  │ Skill-Erkennung/-Generierung│  │  │
│  │  │ erkennung       │  │ /-Ausführung               │  │  │
│  │  └────────┬────────┘  └─────────────┬──────────────┘  │  │
│  └───────────┼─────────────────────────┼─────────────────┘  │
│              │                         │                     │
│  ┌───────────▼─────────────────────────▼─────────────────┐  │
│  │               🧠 Gedächtnissystem (GameMemory)         │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Raum-     │ │Pfad-     │ │Strategie-│ │Spieler-  │ │  │
│  │  │gedächtnis│ │gedächtnis│ │gedächtnis│ │gedächtnis│ │  │
│  │  │Geschützte│ │Erfolgrei-│ │Erfolgrei-│ │Heimat-   │ │  │
│  │  │Bauwerke  │ │che Pfade │ │che       │ │position  │ │  │
│  │  │Gefahren- │ │Fehlschlag│ │Strategien│ │Vorlieben │ │  │
│  │  │zonen     │ │Blacklist │ │Fehlschlag│ │Interak-  │ │  │
│  │  │Ressourcen│ │Erfolgs-  │ │Protokolle│ │tions-    │ │  │
│  │  │          │ │quoten    │ │Kontext-  │ │aufzeich- │ │  │
│  │  │          │ │          │ │Tags      │ │nungen    │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │  │
│  │              Persistente JSON (data/memory/)           │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │ Injection                     │
│  ┌──────────┐ ┌──────────────▼──────┐ ┌──────────────────┐  │
│  │Skill-    │ │ Intelligente        │ │ KI-Entschei-     │  │
│  │Engine    │ │ Navigation          │ │ dungsschicht     │  │
│  │DSL-      │ │ Gedächtnis→Cache→   │ │ Gedächtnis-      │  │
│  │Parsing   │ │ Baritone→A*→        │ │ Kontextinjection │  │
│  │Matching  │ │ Auto-Lernen         │ │ provider.py      │  │
│  └──────────┘ └─────────────────────┘ └──────────────────┘  │
│  ┌──────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │Sicher-   │ │Gesundheits-  │ │ WebUI (Miuix Console)   │ │
│  │heits-    │ │überwachung   │ │ Dunkles Theme/          │ │
│  │prüfung   │ │Drei stufiges │ │ Modell-Konfiguration    │ │
│  │Fünf-     │ │Degradation   │ │                         │ │
│  │stufig    │ │              │ │                         │ │
│  └──────────┘ └──────────────┘ └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Datenfluss-Beispiel

**Gedächtnisgesteuerte intelligente Navigation:**
```
Spieler sagt "nach Hause"
  → Haupt-Agent erkennt Aufgabe [TASK:nach_Hause]
  → Ausführungs-Agent findet passenden go_home Skill
  → SmartNavigator fragt Gedächtnis ab:
      ✅ Heimatposition: (65, 64, -120) aus Spieler-Gedächtnis
      ✅ Cached-Pfad: 3-mal gegangen, Erfolgsquote 100%
      ✅ Geschützte Bauwerke: Um die Basis 30 Blöcke Radius, kein Abbau
      ✅ Gefahrenzone: (80,12,-50) enthält Lava
  → Baritone-Navigation:
      GoalBlock(65, 64, -120)
      + exclusion_zones=[Basis-Schutzzone]
      → Automatischer Umweg, kein Gebäude wird beschädigt
  → Ankunft: Pfad-Cache success_count+1
  → Nächstes Mal nach Hause: Direkt den Cache-Pfad nutzen, null Token-Verbrauch
```

---

## 🧠 Gedächtnissystem

### Drei-Ebenen-Gedächtnisarchitektur

| Ebene | Gespeicherte Inhalte | Persistent | Beispiel |
|-------|---------------------|------------|----------|
| **Raumgedächtnis** | Geschützte Bauwerke, Gefahrenzonen, Ressourcenpunkte, Basis | ✅ JSON | "Basisbereich: (50-100, 60-80, -150--90)" |
| **Pfadgedächtnis** | Erfolgreiche Pfade (Cache), fehlgeschlagene Pfade (Blacklist), Erfolgsquoten | ✅ JSON | "Haus→Mine: über (70,64,-100) Erfolgsquote 100%" |
| **Strategiegedächtnis** | Erfolgreiche Strategien, Fehlschlag-Lektionen, Kontext-Tags | ✅ JSON | "Beim Erzabbau erst Fackeln setzen, dann graben — am effizientesten" |
| **Spieler-Gedächtnis** | Heimatposition, bevorzugte Werkzeuge, Interaktionsaufzeichnungen | ✅ JSON | "Steves Zuhause ist bei (100,64,200)" |
| **Welt-Gedächtnis** | Spawnpunkt, sichere Punkte, wichtige Ereignisse | ✅ JSON | "Spawnpunkt (0,64,0), Liste sicherer Punkte" |

### Automatischer Bauschutz

```python
# Bauschutzzone registrieren (KI darf hier nicht zerstören)
memory.register_building("主城", center=(100, 64, 200), radius=30)
# → Wird bei Navigation automatisch als Baritone exclusion_zones injiziert
# → type: "no_break" + "no_place"
# → KI kann in der Schutzzone keine Blöcke abbauen/setzen

# Automatische Erkennung (alle 60 Sekunden Umgebung scannen)
navigator.auto_detect_and_memorize()
# → Erkennt zusammenhängende Baublöcke → automatisch als Schutzzone registrieren
# → Erkennt Lava/Feuer → automatisch als Gefahrenzone registrieren
# → Erkennt Erzvorkommen → automatisch als Ressourcenpunkt registrieren
```

### Pfad-Cache-Mechanismus

```python
# Erste Navigation: KI plant + führt aus
result = await navigator.goto(100, 64, 200)
# → Pfad gecacht: success_count=1, success_rate=100%

# Zweite Navigation: direkt aus dem Cache
result = await navigator.goto(100, 64, 200)
# → Cache-Treffer, direkt ausgeführt, null Berechnung

# Fehlgeschlagener Pfad: automatisches Lernen
# → fail_count >= 3 → automatisch auf die Blacklist setzen
# → Beim nächsten Mal neu planen, nicht den alten Weg gehen
```

### Automatische Strategie-Ablage

```python
# Nach erfolgreicher Ausführung durch den Ausführungs-Agent automatisch aufzeichnen
memory.record_strategy(
    task_type="mine",
    description="先放火把再挖矿",
    action_sequence=[...],
    success=True,
    context_tags=["nighttime", "cave"],
)

# Beim nächsten gleichen Aufgabentyp automatisch die beste Strategie auswählen
best = memory.get_best_strategy("mine", context_tags=["nighttime"])
# → Gibt die Strategie mit der höchsten Erfolgsquote zurück
```

### KI-Gedächtnis-Kontextinjection

```python
# Bei jeder KI-Entscheidung wird automatisch Gedächtnis injiziert
memory_context = memory.get_ai_context()
# Ausgabe:
# [Gedächtnissystem]
# Basis:
#   - Zuhause: (50, 64, -100) (Radius 30)
# Geschützte Bauwerke (Abbau verboten):
#   - Hauptstadt: (100, 64, 200) (Radius 20)
# Gefahrenzonen:
#   - Lavasee: (80, 12, -50) (lava)
# Bekannte zuverlässige Pfade: 3
# Verifizierte Strategien: 5
```

---

## 🛤️ Intelligente Navigation

### Navigationsablauf

```
SmartNavigator.goto(x, y, z)
  │
  ├── 1. Sicherheitsprüfung
  │     └── Ziel in Schutzzone? → Warnung, aber keine Ablehnung
  │
  ├── 2. Cache-Pfad abfragen
  │     └── Zuverlässiger Cache vorhanden? → Cache-Pfad direkt ausführen
  │
  ├── 3. Navigationskontext abrufen
  │     ├── Ausschlusszonen (geschützte Bauwerke)
  │     ├── Gefahrenzonen (Lava, Klippen)
  │     └── Zuverlässige Pfade als Referenz
  │
  ├── 4. Baritone-Wegfindung (bevorzugt)
  │     ├── exclusion_zones injizieren
  │     ├── Automatisch graben / Brücken bauen / schwimmen
  │     └── Fallkosten / Lava-Vermeidung
  │
  ├── 5. A*-Wegfindung (Fallback)
  │     └── Grundlegendes Grid-A* + Block-Begehbarkeitsprüfung
  │
  └── 6. Ergebnis aufzeichnen
        ├── Erfolg → cache_path(success=True)
        └── Fehlschlag → cache_path(success=False) + ggf. Blacklist
```

### Baritone-Integration

| Eigenschaft | Baritone | Einfaches A* |
|-------------|----------|--------------|
| Wegfindungsalgorithmus | Verbessertes A* + Kosten-Heuristik | Standard-A* |
| Graben | ✅ Automatisch durch Hindernisse | ❌ |
| Brückenbau | ✅ Scaffold-Modus | ❌ |
| Schwimmen | ✅ | ❌ |
| Vertikale Bewegung | ✅ Springen/Leitern/Ranken | ⚠️ Nur 1 Block |
| Lava-Vermeidung | ✅ Kostenstrafe | ❌ |
| Fallkosten | ✅ In Heuristik eingerechnet | ❌ |
| Ausschlusszonen | ✅ `exclusionAreas` | ❌ |
| **Bauschutz** | ✅ `no_break`-Zonen injizieren | ❌ |

### Ausschlusszonentypen

| Typ | Beschreibung | Quelle |
|-----|-------------|--------|
| `no_break` | Blockabbau verboten | Geschützte Bauwerke, Basis |
| `no_place` | Blockplatzierung verboten | Geschützte Bauwerke |
| `avoid` | Vollständig umgehen | Gefahrenzonen (Lava etc.) |

---

## 🤖 Dual-Agent-Architektur

### Warum zwei Agents?

```
Problem mit einem Agent:
  Chat-Kontext + Ausführungskontext → Token-Explosion (>4000/Aufruf)
  Ausführungsfehler kontaminieren den Chat → schlechter Dialog
  Jede Aktion muss den gesamten Chat-Verlauf mitführen → Verschwendung

Zwei-Agent-Lösung:
  Haupt-Agent: nur Chat, gleitendes Fenster von 20 Nachrichten, ~50 Token/Aufruf
  Ausführungs-Agent: zustandslos, frischer Kontext, <1500 Token/Aufruf
```

### Ablauf

```
Spieler-Nachricht
  → Haupt-Agent chattet (persistenter Kontext)
  → Erkennt [TASK:xxx]-Tag
  → Extrahiert Aufgabenbeschreibung
  → Ausführungs-Agent führt aus (zustandslos):
      ├── Skill-Matching
      ├── Gedächtnis-Kontext injizieren
      ├── L1/L2: Cached Skill ausführen
      ├── L3: KI füllt Vorlage + führt aus
      └── L4: KI-Reasoning komplett + führt aus
  → Haupt-Agent formatiert Antwort → Spieler
```

---
## 🚀 Schnellstart

### Systemanforderungen

| Komponente | Anforderung |
|------------|-------------|
| Python | 3.10+ |
| Java | 17+ |
| Minecraft | 1.19.4 - 1.21.4 |
| Fabric Loader | 0.15+ |

---

## 📦 Ein-Klick-Bereitstellung

### Download

Von [GitHub Releases](https://github.com/bmbxwbh/BlockMind/releases/latest) herunterladen:

| Datei | Beschreibung |
|-------|-------------|
| `blockmind-mod-1.0.0.jar` | Fabric Mod (in den Server-Ordner `mods/` legen) |
| `Source code` (zip/tar) | Vollständiger Quellcode |

### Linux / macOS — Ein-Klick-Start

```bash
# Klonen
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

# Ein-Klick-Start (installiert automatisch Abhängigkeiten + MC-Server + BlockMind + WebUI)
chmod +x start.sh
./start.sh
```

> `start.sh` führt automatisch aus: Python/Java erkennen → Abhängigkeiten installieren → Vorhandenen MC-Server suchen → Version auswählen und installieren → Alles starten

### Windows — Ein-Klick-Start

```cmd
:: Klonen (oder ZIP herunterladen und entpacken)
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

:: Ein-Klick-Installation
install.bat

:: Ein-Klick-Start (MC-Server + BlockMind + WebUI)
start_all.bat
```

> Detaillierte Schritte siehe [Windows-Bereitstellungshandbuch](docs/WINDOWS.md)

### Docker-Bereitstellung

```bash
# Image pullen
docker pull ghcr.io/bmbxwbh/blockmind:latest

# Konfigurationsvorlage herunterladen
wget https://raw.githubusercontent.com/bmbxwbh/BlockMind/main/config.example.yaml -O config.yaml
# config.yaml bearbeiten und deine KI-Modell-Konfiguration eintragen

# Starten
docker run -d \
  --name blockmind \
  -p 19951:19951 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v blockmind-data:/data \
  ghcr.io/bmbxwbh/blockmind:latest
```

Oder mit docker-compose:

```bash
git clone https://github.com/bmbxwbh/BlockMind.git && cd BlockMind
cp config.example.yaml config.yaml
# config.yaml bearbeiten
docker compose up -d
```

```bash
# Logs anzeigen
docker compose logs -f blockmind
# Stoppen
docker compose down
```

### Konfiguration

`config.yaml` bearbeiten:

```yaml
ai:
  main_agent:
    provider: "openai"          # openai oder anthropic
    api_key: "sk-your-key"
    model: "gpt-4o"             # Dein Modellname
    base_url: ""                # Eigene API-Adresse (optional)

webui:
  enabled: true
  port: 19951
  auth:
    password: "your-password"   # WebUI-Anmeldepasswort
```

Nach dem Start unter `http://localhost:19951` die Konsole öffnen.

---

## 🔌 Fabric Mod API

### Statusabfragen

| Endpunkt | Methode | Beschreibung |
|----------|---------|-------------|
| `/health` | GET | Gesundheitsprüfung |
| `/api/status` | GET | Spielerstatus |
| `/api/world` | GET | Weltstatus |
| `/api/inventory` | GET | Inventarinformationen |
| `/api/entities?radius=32` | GET | Nahe Entitäten |
| `/api/blocks?radius=16` | GET | Nahe Blöcke |

### Aktionsausführung

| Endpunkt | Methode | Beschreibung |
|----------|---------|-------------|
| `/api/move` | POST | Zu Koordinaten bewegen |
| `/api/dig` | POST | Block abbauen |
| `/api/place` | POST | Block platzieren |
| `/api/attack` | POST | Entität angreifen |
| `/api/eat` | POST | Essen |
| `/api/look` | POST | In Richtung einer Koordinate schauen |
| `/api/chat` | POST | Chat-Nachricht senden |

### Wegfindung

| Endpunkt | Methode | Beschreibung |
|----------|---------|-------------|
| `/api/pathfind` | POST | Pfadnavigation (Baritone/A*) |
| `/api/pathfind/stop` | POST | Navigation stoppen |
| `/api/pathfind/status` | GET | Navigationsstatus |

### Event-Push

Der Mod sendet Events über WebSocket:
- `player_damaged` — Spieler nimmt Schaden
- `entity_attack` — Wird angegriffen
- `health_low` — Gesundheit niedrig
- `inventory_full` — Inventar voll
- `block_broken` — Blockabbau abgeschlossen

---

## 📝 Skill-DSL-System

### Aufgabenklassifikation

| Stufe | Typ | Beispiel | Cache-Strategie |
|-------|-----|----------|----------------|
| L1 | Feste Aufgabe | "nach Hause" | Direkt ausführen |
| L2 | Parametrisierte Aufgabe | "10 Diamanten abbauen" | Parametrierter Cache |
| L3 | Vorlagen-Aufgabe | "Eine Unterkunft bauen" | Vorlagen-Matching |
| L4 | Dynamische Aufgabe | "Hilf mir, den Enderdrachen zu besiegen" | KI-Reasoning |

### Skill-YAML-Beispiel

```yaml
skill_id: mine_diamonds
name: "Diamanten abbauen"
level: L2
parameters:
  count: {type: int, default: 10, min: 1, max: 64}
steps:
  - action: pathfind
    target: {y: -59}
    note: "Zur Diamant-Ebene navigieren"
  - action: dig_loop
    block: diamond_ore
    count: ${count}
  - action: pathfind
    target: home
    note: "Zurück zur Basis"
```

---

## 🛡️ Sicherheitssystem

| Ebene | Mechanismus | Beschreibung |
|-------|------------|-------------|
| L1 | Risikobewertung | Jede Aktion wird mit 0-100 bewertet |
| L2 | Aktionsgenehmigung | Hohe Risiken erfordern Bestätigung |
| L3 | Notfall-Übernahme | Spieler kann die KI jederzeit unterbrechen |
| L4 | Audit-Protokoll | Alle Aktionen sind nachverfolgbar |
| L5 | Sicherheitszonen-Beschränkung | Begrenzung von Zerstörungs-/Platzierungsradius |

---

## 🖥️ WebUI-Konsole

Nach dem Start unter `http://localhost:19951` verfügbar, unterstützt:

- 📊 Dashboard — Echtzeit-Statusüberwachung
- 🛠️ Skill-Verwaltung — YAML online bearbeiten
- 🧠 Gedächtnissystem — Ansehen/Bereinigen/Sichern
- 🤖 Modell-Konfiguration — KI-Modell im laufenden Betrieb wechseln
- 💬 Befehlskonsole — Natürlichsprachliche Befehle
- 📋 Aufgabenwarteschlange — Ausführungsstatus einsehen
- 📝 Protokollzentrale — Echtzeit-Log-Stream

---

## ❓ FAQ

**F: Muss Baritone installiert sein?**
A: Nein. Baritone ist eine optionale Abhängigkeit. Ohne Baritone wird automatisch auf einfache Geradeaus-Navigation mit A* zurückgegriffen.

**F: Wo werden die Gedächtnisdaten gespeichert?**
A: Im Verzeichnis `data/memory/` als 5 JSON-Dateien, die sitzungsübergreifend erhalten bleiben.

**F: Wie wird der Bauschutz aktiv?**
A: Auf zwei Wegen: ① Manuell registrieren ② Automatische Erkennung (alle 60 Sekunden Scan).

**F: Welche KI-Anbieter werden unterstützt?**
A: OpenAI-kompatibles Format (einschließlich DeepSeek/OpenRouter/MiMo etc.) + Anthropic-Format.

**F: Wie groß ist das Docker-Image?**
A: Etwa 200MB, basiert auf einem mehrstufigen Build mit python:3.11-slim.

---

## 🗺️ Roadmap

### v3.0 (aktuell) ✅
- [x] Drei-Ebenen-Gedächtnissystem (Raum/Pfad/Strategie)
- [x] Intelligente Navigation (gedächtnisgesteuert + Baritone-Integration)
- [x] Dual-Agent-Architektur (Chat/Ausführung getrennt)
- [x] Automatischer Bauschutz
- [x] Miuix Console WebUI
- [x] Windows/Linux Ein-Klick-Bereitstellung
- [x] Docker-Image + GHCR automatische Veröffentlichung
- [x] GitHub Actions CI/CD

### v3.1 (geplant)
- [ ] Multimodale Eingabe (Screenshot-Analyse)
- [ ] Skill-Marktplatz (Import/Export)
- [ ] Mehrspieler-Zusammenarbeit
- [ ] Sprachinteraktion

---

## 📄 Lizenz

MIT License. Details siehe [LICENSE](LICENSE).
