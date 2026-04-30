# 🧠 BlockMind — Sistema di Compagno di Gioco Intelligente per Minecraft

> **Fabric Mod + Guidato da AI + Sistema di Memoria** · v3.0 · 2026-04-30

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![Fabric](https://img.shields.io/badge/Fabric-0.92+-yellow.svg)](https://fabricmc.net)
[![MC](https://img.shields.io/badge/Minecraft-1.20.x--1.21.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**In una frase:** Fabric Mod fornisce interfacce di gioco precise + backend Python guida le decisioni AI + il sistema di memoria consente l'apprendimentointer-sessione, realizzando un compagno di gioco intelligente per Minecraft in grado di sopravvivere autonomamente 7×24.

🌐 [中文](README.md) | [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | [Español](README-es.md) | [Français](README-fr.md) | [Bahasa Indonesia](README-id.md) | **Italiano** | [Português](README-pt.md) | [Русский](README-ru.md) | [ภาษาไทย](README-th.md) | [Türkçe](README-tr.md) | [Tiếng Việt](README-vi.md)
---

## 📖 Indice

- [Caratteristiche del Progetto](#-caratteristiche-del-progetto)
- [Architettura del Sistema](#-architettura-del-sistema)
- [Sistema di Memoria](#-sistema-di-memoria)
- [Navigazione Intelligente](#-navigazione-intelligente)
- [Architettura Doppio Agente](#-architettura-doppio-agente)
- [Guida Rapida](#-guida-rapida)
- [Deploy con Un Click](#-deploy-con-un-click)
- [API del Fabric Mod](#-api-del-fabric-mod)
- [Sistema Skill DSL](#-sistema-skill-dsl)
- [Sistema di Sicurezza](#-sistema-di-sicurezza)
- [Pannello di Controllo WebUI](#-pannello-di-controllo-webui)
- [Guida al Deploy](#-guida-al-deploy)
- [FAQ](#-faq)
- [Roadmap](#-roadmap)

---

## ✨ Caratteristiche del Progetto

### 🧠 Sistema di Memoria — Apprendimentointer-sessione (Nuovo in v3.0)

```
Metodo tradizionale:  Dimentica tutto ad ogni riavvio, ripete gli stessi errori, spreca Token
Con memoria:  Memoria spaziale/percorso/strategia a tre livelli, JSON persistente, riutilizzointer-sessione
```

- **Memoria spaziale**: Rileva e ricorda automaticamente zone protette degli edifici, aree pericolose, punti risorsa
- **Memoria dei percorsi**: Cache dei percorsi riusciti, blacklist di quelli falliti, statistiche di successo
- **Memoria strategica**: Le operazioni riuscite si consolidano automaticamente in strategie riutilizzabili, riutilizzo a zero Token
- **Protezione edifici**: Evita automaticamente gli edifici dei giocatori durante la navigazione, niente più paura di distruggere le basi

### 🛤️ Navigazione Intelligente — Pathfinding guidato dalla memoria (Nuovo in v3.0)

```
Metodo tradizionale:  walk_to(x,y,z) → si blocca contro un muro / distrugge un edificio
Navigazione intelligente:  consulta memoria → usa cache → Baritone (escludi zone protette) → fallback A*
```

- **Priorità alla cache**: I percorsi già percorsi vengono riutilizzati direttamente, zero calcoli
- **Integrazione Baritone**: Il motore di pathfinding più potente della community, scava automaticamente/costruisce ponti/nuota/evita lava
- **Iniezione zone protette**: Gli edifici in memoria vengono iniettati automaticamente come zone di esclusione Baritone
- **Apprendimento automatico**: Ogni risultato di navigazione viene registrato automaticamente nel sistema di memoria

### 🤖 Architettura Doppio Agente — Isolamento chat ed esecuzione (Nuovo in v2.0)

```
Agente principale:  Gestisce la chat, contesto persistente, solo riconoscimento intenti (~50 Token/volta)
Agente operativo:  Gestisce l'esecuzione, senza stato, contesto nuovo (<1500 Token/volta)
```

- **Agente principale**: Mantiene il contesto della conversazione, identifica i tag `[TASK:xxx]`
- **Agente operativo**: Senza stato, usa e getta, evita l'esplosione del contesto
- **Iniezione memoria**: Durante le decisioni AI, il contesto della memoria viene iniettato automaticamente (zone protette, percorsi noti, ecc.)

### 🔌 Architettura Fabric Mod — Precisa e affidabile

- **Zero parsing protocollo**: Chiama direttamente le API interne del gioco
- **13 endpoint HTTP** + eventi WebSocket in tempo reale
- **Integrazione Baritone opzionale**: Con Baritone pathfinding avanzato, senza pathfinding lineare base

### 🛡️ Sistema di Sicurezza a Cinque Livelli

| Livello | Nome | Esempio | Strategia |
|---------|------|---------|-----------|
| 0 | Completamente sicuro | Movimento, salto | Esecuzione automatica |
| 1 | Basso rischio | Scavare terra, posare torce | Esecuzione automatica |
| 2 | Medio rischio | Estrarre minerali, attaccare creature neutrali | Esecuzione automatica |
| 3 | Alto rischio | Accendere TNT, posare lava | Richiede autorizzazione del giocatore |
| 4 | Rischio fatale | Posare blocchi comando | Vietato per impostazione predefinita |

---

## 🏗️ Architettura del Sistema

```
┌──────────────────────────────────────────────────────────────┐
│                    Server Minecraft                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            BlockMind Fabric Mod (Java)                 │  │
│  │                                                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Collector │ │Esecutore │ │Listener  │ │Baritone  │ │  │
│  │  │Stato     │ │Azione    │ │Evento    │ │Motore    │ │  │
│  │  │Blocchi/  │ │Muovi/    │ │Chat/     │ │Pathfind  │ │  │
│  │  │Entità/   │ │Scava/    │ │Danno/    │ │(opzionale│ │  │
│  │  │Inventario│ │Posa/Attac│ │Blocchi   │ │)         │ │  │
│  │  │/Mondo    │ │ca        │ │          │ │          │ │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │  │
│  │       └─────────────┼────────────┼────────────┘       │  │
│  │               HTTP API :25580 + WebSocket              │  │
│  └─────────────────────────────┼──────────────────────────┘  │
└────────────────────────────────┼─────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────┐
│                  BlockMind Backend Python                     │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │               Architettura Doppio Agente               │  │
│  │  ┌─────────────────┐  ┌────────────────────────────┐  │  │
│  │  │Agente Principale│  │ Agente Operativo           │  │  │
│  │  │(Chat)           │  │ (Esecuzione, senza stato)   │  │  │
│  │  │Contesto persist.│  │ Contesto nuovo ogni volta  │  │  │
│  │  │Riconoscimento   │  │ Matching/Generazione/      │  │  │
│  │  │intenti          │  │ Esecuzione Skill           │  │  │
│  │  └────────┬────────┘  └─────────────┬──────────────┘  │  │
│  └───────────┼─────────────────────────┼─────────────────┘  │
│              │                         │                     │
│  ┌───────────▼─────────────────────────▼─────────────────┐  │
│  │               🧠 Sistema di Memoria (GameMemory)       │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Memoria   │ │Memoria   │ │Memoria   │ │Memoria   │ │  │
│  │  │Spaziale  │ │Percorsi  │ │Strategia │ │Giocatore │ │  │
│  │  │Zone prot.│ │Percorsi  │ │Strategie │ │Pos. base │ │  │
│  │  │Aree peric│ │riusciti  │ │riuscite  │ │Preferenze│ │  │
│  │  │Punti ris.│ │Blacklist │ │Registro  │ │Interaz.  │ │  │
│  │  │          │ │% successo│ │fallimenti│ │          │ │  │
│  │  │          │ │          │ │Tag contex│ │          │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │  │
│  │              JSON persistente (data/memory/)            │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │ Iniezione                     │
│  ┌──────────┐ ┌──────────────▼──────┐ ┌──────────────────┐  │
│  │Motore    │ │Navigazione          │ │Livello Decisione │  │
│  │Skill     │ │Intelligente         │ │AI                │  │
│  │Parsing   │ │Memoria→Cache→       │ │Iniezione contesto│  │
│  │Matching  │ │Baritone→Fallback A* │ │memoria           │  │
│  │Esecuzione│ │→Auto-apprendimento  │ │provider.py       │  │
│  └──────────┘ └─────────────────────┘ └──────────────────┘  │
│  ┌──────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │Verifica  │ │Monitoraggio  │ │ WebUI (Miuix Console)   │ │
│  │Sicurezza │ │Salute        │ │Tema scuro/Config modello│ │
│  │Controllo │ │Degrado a     │ │                         │ │
│  │rischio 5 │ │3 livelli     │ │                         │ │
│  │livelli   │ │              │ │                         │ │
│  └──────────┘ └──────────────┘ └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Esempio di Flusso Dati

**Navigazione intelligente guidata dalla memoria:**
```
Il giocatore dice "vai a casa"
  → L'Agente Principale identifica il compito [TASK:vai a casa]
  → L'Agente Operativo corrisponde alla Skill go_home
  → SmartNavigator consulta la memoria:
      ✅ Posizione casa: (65, 64, -120) dalla memoria del giocatore
      ✅ Percorso in cache: percorso 3 volte, tasso successo 100%
      ✅ Zona protetta edificio: 30 blocchi attorno alla base, nessuna distruzione
      ✅ Zona pericolosa: (80,12,-50) c'è lava
  → Navigazione Baritone:
      GoalBlock(65, 64, -120)
      + exclusion_zones=[zona protetta base]
      → Devia automaticamente, non distrugge nessun edificio
  → All'arrivo: cache percorso success_count+1
  → La prossima volta per andare a casa: usa direttamente il percorso in cache, zero consumo Token
```

---

## 🧠 Sistema di Memoria

### Architettura della Memoria a Tre Livelli

| Livello | Contenuto Memorizzato | Persistente | Esempio |
|---------|----------------------|-------------|---------|
| **Memoria Spaziale** | Zone protette edifici, aree pericolose, punti risorsa, base | ✅ JSON | "Area base: (50-100, 60-80, -150--90)" |
| **Memoria Percorsi** | Cache percorsi riusciti, blacklist percorsi falliti, tasso successo | ✅ JSON | "Casa→Miniera: passa per (70,64,-100) tasso successo 100%" |
| **Memoria Strategica** | Consolidamento strategie riuscite, lezioni dai fallimenti, tag contesto | ✅ JSON | "Quando mina, prima posa la torca poi scava, massima efficienza" |
| **Memoria Giocatore** | Posizione casa, strumenti preferiti, registro interazioni | ✅ JSON | "La casa di Steve è a (100,64,200)" |
| **Memoria Mondo** | Punto di spawn, punti sicuri, eventi importanti | ✅ JSON | "Punto di spawn (0,64,0), lista punti sicuri" |

### Protezione Automatica degli Edifici

```python
# Registra zona protetta edificio (vieta la distruzione da parte dell'AI)
memory.register_building("città_principale", center=(100, 64, 200), radius=30)
# → Iniezione automatica come exclusion_zones Baritone durante la navigazione
# → type: "no_break" + "no_place"
# → L'AI non può distruggere/posare blocchi nella zona protetta

# Rilevamento automatico (scansione ogni 60 secondi)
navigator.auto_detect_and_memorize()
# → Rileva blocchi edificio consecutivi → registra automaticamente come zona protetta
# → Rileva lava/fuoco → registra automaticamente come zona pericolosa
# → Rileva accumulo minerali → registra automaticamente come punto risorsa
```

### Meccanismo di Cache dei Percorsi

```python
# Prima navigazione: pianificazione AI + esecuzione
result = await navigator.goto(100, 64, 200)
# → Percorso in cache: success_count=1, success_rate=100%

# Seconda navigazione: usa direttamente la cache
result = await navigator.goto(100, 64, 200)
# → Cache hit, esecuzione diretta, zero calcoli

# Percorsi falliti: apprendimento automatico
# → fail_count >= 3 → aggiunto automaticamente alla blacklist
# → La prossima volta ripianifica, non usa il vecchio percorso
```

### Consolidamento Automatico delle Strategie

```python
# Dopo l'esecuzione riuscita dell'Agente Operativo, registra automaticamente
memory.record_strategy(
    task_type="mine",
    description="Prima posa la torca poi scava",
    action_sequence=[...],
    success=True,
    context_tags=["nighttime", "cave"],
)

# Alla prossima stessa tipologia di compito, corrisponde automaticamente la strategia migliore
best = memory.get_best_strategy("mine", context_tags=["nighttime"])
# → Restituisce la strategia con il tasso di successo più alto
```

### Iniezione del Contesto Memoria nell'AI

```python
# Ad ogni decisione AI, il contesto memoria viene iniettato automaticamente
memory_context = memory.get_ai_context()
# Output:
# [Sistema di Memoria]
# Base:
#   - Casa: (50, 64, -100) (raggio 30)
# Zone protette edifici (distruzione vietata):
#   - Città principale: (100, 64, 200) (raggio 20)
# Aree pericolose:
#   - Lago di lava: (80, 12, -50) (lava)
# Percorsi affidabili noti: 3
# Strategie verificate: 5
```

---

## 🛤️ Navigazione Intelligente

### Flusso di Navigazione

```
SmartNavigator.goto(x, y, z)
  │
  ├── 1. Controllo sicurezza
  │     └── La destinazione è in una zona protetta? → Avvisa ma non rifiuta
  │
  ├── 2. Consulta cache percorsi
  │     └── Cache affidabile disponibile? → Esegue direttamente il percorso in cache
  │
  ├── 3. Ottieni contesto navigazione
  │     ├── Zone di esclusione (zone protette edifici)
  │     ├── Aree pericolose (lava, precipizi)
  │     └── Riferimenti percorso affidabili
  │
  ├── 4. Pathfinding Baritone (prioritario)
  │     ├── Iniezione exclusion_zones
  │     ├── Scava automaticamente / Costruisci ponti / Nuota
  │     └── Costo caduta / Evita lava
  │
  ├── 5. Pathfinding A* (fallback)
  │     └── A* griglia base + valutazione blocco attraversabile
  │
  └── 6. Registra risultato
        ├── Successo → cache_path(success=True)
        └── Fallimento → cache_path(success=False) + possibile blacklist
```

### Integrazione Baritone

| Caratteristica | Baritone | A* Base |
|----------------|----------|---------|
| Algoritmo pathfinding | A* migliorato + euristica costo | A* standard |
| Scavare tunnel | ✅ Scava automaticamente attraverso ostacoli | ❌ |
| Costruire ponti | ✅ Modalità scaffold | ❌ |
| Nuoto | ✅ | ❌ |
| Movimento verticale | ✅ Salto/Scale/Corde | ⚠️ Solo 1 blocco |
| Evita lava | ✅ Penalità costo | ❌ |
| Costo caduta | ✅ Inserito nella funzione euristica | ❌ |
| Zone di esclusione | ✅ `exclusionAreas` | ❌ |
| **Protezione edifici** | ✅ Iniezione zone `no_break` | ❌ |

### Tipi di Zone di Esclusione

| Tipo | Descrizione | Fonte |
|------|-------------|-------|
| `no_break` | Vieta la distruzione di blocchi | Zone protette edifici, base |
| `no_place` | Vieta il posizionamento di blocchi | Zone protette edifici |
| `avoid` | Evita completamente | Aree pericolose (lava ecc.) |

---

## 🤖 Architettura Doppio Agente

### Perché servono due Agenti?

```
Problema dell'Agente singolo:
  Contesto chat + Contesto operazione → Esplosione Token (>4000/volta)
  Fallimento operazione contamina la chat → Esperienza conversazione scarsa
  Ogni operazione deve portare la cronologia chat completa → Spreco

Soluzione Doppio Agente:
  Agente Principale: solo chat, finestra scorrevole 20 messaggi, ~50 Token/volta
  Agente Operativo: senza stato, contesto nuovo, <1500 Token/volta
```

### Flusso

```
Messaggio del giocatore
  → Agente Principale chat (contesto persistente)
  → Rilevato tag [TASK:xxx]
  → Estrai descrizione compito
  → Agente Operativo esegue (senza stato):
      ├── Matching Skill
      ├── Iniezione contesto memoria
      ├── L1/L2: Esecuzione Skill in cache
      ├── L3: AI compila template + esegue
      └── L4: Ragionamento completo AI + esegue
  → Agente Principale formatta risposta → Giocatore
```

---
## 🚀 Guida Rapida

### Requisiti di Sistema

| Componente | Requisito |
|------------|-----------|
| Python | 3.10+ |
| Java | 17+ |
| Minecraft | 1.19.4 - 1.21.4 |
| Fabric Loader | 0.15+ |

---

## 📦 Deploy con Un Click

### Download

Scarica da [GitHub Releases](https://github.com/bmbxwbh/BlockMind/releases/latest):

| File | Descrizione |
|------|-------------|
| `blockmind-mod-1.0.0.jar` | Fabric Mod (inserire nella cartella mods/ del server) |
| `Source code` (zip/tar) | Codice sorgente completo |

### Avvio rapido Linux / macOS

```bash
# Clona
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

# Avvio rapido (installa automaticamente dipendenze + server MC + BlockMind + WebUI)
chmod +x start.sh
./start.sh
```

> `start.sh` esegue automaticamente: rileva Python/Java → installa dipendenze → cerca server MC esistente → sceglie versione e installa → avvia tutto

### Avvio rapido Windows

```cmd
:: Clona (o scarica zip ed estrai)
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

:: Installazione rapida
install.bat

:: Avvio rapido (server MC + BlockMind + WebUI)
start_all.bat
```

> Vedi la [Guida al Deploy Windows](docs/WINDOWS.md) per i dettagli.

### Deploy Docker

```bash
# Scarica immagine
docker pull ghcr.io/bmbxwbh/blockmind:latest

# Scarica template configurazione
wget https://raw.githubusercontent.com/bmbxwbh/BlockMind/main/config.example.yaml -O config.yaml
# Modifica config.yaml inserendo la configurazione del tuo modello AI

# Avvia
docker run -d \
  --name blockmind \
  -p 19951:19951 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v blockmind-data:/data \
  ghcr.io/bmbxwbh/blockmind:latest
```

Oppure usa docker-compose:

```bash
git clone https://github.com/bmbxwbh/BlockMind.git && cd BlockMind
cp config.example.yaml config.yaml
# Modifica config.yaml
docker compose up -d
```

```bash
# Visualizza log
docker compose logs -f blockmind
# Arresta
docker compose down
```

### Configurazione

Modifica `config.yaml`:

```yaml
ai:
  main_agent:
    provider: "openai"          # openai o anthropic
    api_key: "sk-your-key"
    model: "gpt-4o"             # Nome del tuo modello
    base_url: ""                # URL API personalizzato (opzionale)

webui:
  enabled: true
  port: 19951
  auth:
    password: "your-password"   # Password di accesso WebUI
```

Dopo l'avvio, visita `http://localhost:19951` per accedere al pannello di controllo.

---

## 🔌 API del Fabric Mod

### Query di Stato

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/health` | GET | Controllo salute |
| `/api/status` | GET | Stato giocatore |
| `/api/world` | GET | Stato mondo |
| `/api/inventory` | GET | Informazioni inventario |
| `/api/entities?radius=32` | GET | Entità nelle vicinanze |
| `/api/blocks?radius=16` | GET | Blocchi nelle vicinanze |

### Esecuzione Azioni

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/api/move` | POST | Spostati alle coordinate |
| `/api/dig` | POST | Scava blocco |
| `/api/place` | POST | Posiziona blocco |
| `/api/attack` | POST | Attacca entità |
| `/api/eat` | POST | Mangia |
| `/api/look` | POST | Guarda verso coordinate |
| `/api/chat` | POST | Invia messaggio chat |

### Pianificazione Percorso

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/api/pathfind` | POST | Navigazione percorso (Baritone/A*) |
| `/api/pathfind/stop` | POST | Ferma navigazione |
| `/api/pathfind/status` | GET | Stato navigazione |

### Push Eventi

Il Mod invia eventi tramite WebSocket:
- `player_damaged` — Giocatore ferito
- `entity_attack` — Sotto attacco
- `health_low` — Vita bassa
- `inventory_full` — Inventario pieno
- `block_broken` — Scavo blocco completato

---

## 📝 Sistema Skill DSL

### Classificazione dei Compiti

| Livello | Tipo | Esempio | Strategia Cache |
|---------|------|---------|-----------------|
| L1 | Compito fisso | "vai a casa" | Esecuzione diretta |
| L2 | Compito parametrizzato | "estrai 10 diamanti" | Cache con parametri |
| L3 | Compito template | "costruisci un rifugio" | Matching template |
| L4 | Compito dinamico | "aiutami a sconfiggere l'Ender Dragon" | Ragionamento AI |

### Esempio Skill YAML

```yaml
skill_id: mine_diamonds
name: "estrai diamanti"
level: L2
parameters:
  count: {type: int, default: 10, min: 1, max: 64}
steps:
  - action: pathfind
    target: {y: -59}
    note: "Vai al livello dei diamanti"
  - action: dig_loop
    block: diamond_ore
    count: ${count}
  - action: pathfind
    target: home
    note: "Torna alla base"
```

---

## 🛡️ Sistema di Sicurezza

| Livello | Meccanismo | Descrizione |
|---------|------------|-------------|
| L1 | Valutazione rischio | Ogni azione punteggiata 0-100 |
| L2 | Autorizzazione operazioni | Alto rischio richiede conferma |
| L3 | Presa in carico d'emergenza | Il giocatore può interrompere l'AI in qualsiasi momento |
| L4 | Log di audit | Tutte le operazioni tracciabili |
| L5 | Limitazione zona sicura | Limita area distruzione/posizionamento |

---

## 🖥️ Pannello di Controllo WebUI

Dopo l'avvio, visita `http://localhost:19951`, supporta:

- 📊 Dashboard — Monitoraggio stato in tempo reale
- 🛠️ Gestione Skill — Modifica YAML online
- 🧠 Sistema di Memoria — Visualizza/Pulisci/Backup
- 🤖 Configurazione Modello — Cambio modello AI a caldo
- 💬 Pannello Comandi — Istruzioni in linguaggio naturale
- 📋 Coda Compiti — Visualizza stato esecuzione
- 📝 Centro Log — Flusso log in tempo reale

---

## ❓ FAQ

**Q: Devo installare Baritone?**
A: No, è opzionale. Senza Baritone, il sistema torna automaticamente al movimento lineare base A*.

**Q: Dove sono memorizzati i dati della memoria?**
A: Nella directory `data/memory/`, 5 file JSON, conservatiinter-sessione.

**Q: Come funziona la protezione degli edifici?**
A: Due modalità: ① Registrazione manuale ② Rilevamento automatico (scansione ogni 60 secondi).

**Q: Quali provider AI sono supportati?**
A: Formato compatibile OpenAI (inclusi DeepSeek/OpenRouter/MiMo ecc.) + Formato Anthropic.

**Q: Quanto è grande l'immagine Docker?**
A: Circa 200MB, basata su build multi-stadio python:3.11-slim.

---

## 🗺️ Roadmap

### v3.0 (Attuale) ✅
- [x] Sistema di memoria a tre livelli (spaziale/percorso/strategia)
- [x] Navigazione intelligente (guidata dalla memoria + integrazione Baritone)
- [x] Architettura doppio agente (isolamento chat/esecuzione)
- [x] Protezione automatica zone edifici
- [x] Miuix Console WebUI
- [x] Deploy con un click Windows/Linux
- [x] Immagine Docker + pubblicazione automatica GHCR
- [x] GitHub Actions CI/CD

### v3.1 (In pianificazione)
- [ ] Input multimodale (analisi screenshot)
- [ ] Mercato Skill (importa/esporta)
- [ ] Collaborazione multiplayer
- [ ] Interazione vocale

---

## 📄 Licenza

MIT License. Vedi [LICENSE](LICENSE) per i dettagli.
