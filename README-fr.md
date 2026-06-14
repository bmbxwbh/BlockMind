# 🧠 BlockMind

> **Mod Fabric + IA + Système de mémoire** · Compagnon intelligent Minecraft

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![MC](https://img.shields.io/badge/Minecraft-1.20~26.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT--NC-purple.svg)](LICENSE)

Le Mod Fabric fournit des interfaces de jeu précises + le backend Python pilote les décisions de l'IA + le système de mémoire apprend entre les sessions. **Supporte serveur et client**, utilisable en solo, en LAN ou sur serveur.

🌐 [中文](README.md) | [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | [Español](README-es.md) | **Français**

---

## Pourquoi BlockMind

### 1. Système de mémoire — L'IA apprend

Les compagnons IA traditionnels oublient tout au redémarrage. BlockMind dispose de trois couches de mémoire persistante :

- **Mémoire spatiale** : Retient automatiquement les zones de construction protégées, les zones dangereuses et les points de ressources
- **Mémoire de chemin** : Met en cache les chemins réussis, met en liste noire les échoués, réutilisation ultérieure
- **Mémoire stratégique** : Les opérations réussies se consolident en stratégies réutilisables, consommation de tokens zéro

L'IA navigue en évitant automatiquement les constructions du joueur, ne détruit jamais la maison.

### 2. Architecture à double Agent — Économie de tokens

```
Agent principal (~50 tokens/appel) : Chat uniquement + identification d'intention
Agent d'opération (<1500 tokens/appel) : Exécution sans état, jetable
```

Comparé à un agent unique (>4000 tokens/appel), économie de 84% des coûts.

### 3. Serveur + Client dual

| Mode | Emplacement | Joueur | Scénario |
|------|-------------|--------|----------|
| Serveur | `mods/` du serveur | FakePlayer (Bot) | Serveur 7×24 |
| Client | `mods/` du client | Joueur local | Solo / LAN |

### 4. Baritone intégré + protection des constructions

L'IA utilise Baritone pour le pathfinding (creusage/ponts/nage automatiques), mais contourne automatiquement les zones de construction protégées. Les bâtiments en mémoire sont injectés comme zones d'exclusion Baritone en temps réel.

### 5. Skill DSL + marketplace

Définissez des compétences IA réutilisables en YAML (minage, agriculture, construction), partagées avec la communauté. Les compétences générées par l'IA sont sauvegardées automatiquement, exécution sans tokens la prochaine fois.

---

## Démarrage rapide

### Prérequis

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

### Configuration

Éditez `config.yaml` :

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

Accédez à `http://localhost:19951` pour le panneau de contrôle.

---

## Architecture

```
┌──────────────── Minecraft ────────────────┐
│  BlockMind Fabric Mod (Java)              │
│  Collecte · Exécution · Événements        │
│  HTTP API :25580 · WebSocket              │
└──────────────────┬────────────────────────┘
                   │
┌──────────────────▼────────────────────────┐
│  Backend Python BlockMind                 │
│  ┌──────────┐  ┌──────────────────────┐  │
│  │Agent     │  │Agent d'opération     │  │
│  │principal │  │(sans état)           │  │
│  │Chat+iden.│  │Match/exéc. Skills    │  │
│  └─────┬────┘  └──────────┬───────────┘  │
│  ┌─────▼──────────────────▼───────────┐  │
│  │Mémoire · Navigation · Skills       │  │
│  └────────────────┬───────────────────┘  │
│  ┌────────────────▼───────────────────┐  │
│  │WebUI (MiuiX)                      │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## Panneau de contrôle WebUI

`http://localhost:19951` — Icônes Lucide + thème sombre MiuiX

| Fonction | Description |
|----------|-------------|
| Dashboard | État en temps réel, raccourcis, flux d'événements |
| Skills | Édition YAML en ligne, exécution en un clic |
| Marketplace | Parcourir/installer/importer/exporter les skills communautaires |
| Mémoire | Voir/sauvegarder/nettoyer/importer/exporter |
| Modèles | Configuration dual des agents, basculement à chaud |
| Sécurité | Niveaux de risque, journal d'audit |
| File de tâches | Surveillance de l'état d'exécution |
| Logs | Flux de logs en temps réel via WebSocket |

---

## API Fabric Mod

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/status` | GET | État du joueur |
| `/api/inventory` | GET | Informations d'inventaire |
| `/api/entities` | GET | Entités à proximité |
| `/api/move` | POST | Déplacer vers des coordonnées |
| `/api/dig` | POST | Creuser un bloc |
| `/api/place` | POST | Poser un bloc |
| `/api/attack` | POST | Attaquer une entité |
| `/api/chat` | POST | Envoyer un message |

Documentation complète dans [API Fabric Mod](docs/MOD_BUILD.md).

---

## Versions supportées

| MC | Java | État |
|----|------|------|
| 1.20.0 ~ 1.20.6 | 17~21 | ✅ |
| 1.21 ~ 1.21.4 | 21 | ✅ |
| 26.1 ~ 26.1.2 | 25 | ✅ Dernière |

---

## FAQ

**Baritone est-il obligatoire ?** Non, sans lui le système utilise A* basique.

**Où sont stockées les données de mémoire ?** Dans `data/memory/`, 5 fichiers JSON.

**Quels modèles d'IA sont supportés ?** Format OpenAI (DeepSeek/OpenRouter/MiMo) + Anthropic.

**Utilisable en mode solo ?** Oui, placez le Mod dans `mods/` du client.

---

## Licence

MIT-NC — Usage non commercial. Voir [LICENSE](LICENSE).
