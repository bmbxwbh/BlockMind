# 🧠 BlockMind — Système de compagnon IA intelligent pour Minecraft

> **Fabric Mod + Propulsé par IA + Système de mémoire** · v3.0 · 2026-04-30

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![Fabric](https://img.shields.io/badge/Fabric-0.92+-yellow.svg)](https://fabricmc.net)
[![MC](https://img.shields.io/badge/Minecraft-1.20.x--1.21.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**En résumé :** Fabric Mod fournit des interfaces de jeu précises + un backend Python propulsant les décisions de l'IA + un système de mémoire permettant l'apprentissage inter-sessions, pour un compagnon Minecraft autonome opérant 24h/24, 7j/7.

🌐 [中文](README.md) | [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | [Español](README-es.md) | **Français** | [Bahasa Indonesia](README-id.md) | [Italiano](README-it.md) | [Português](README-pt.md) | [Русский](README-ru.md) | [ภาษาไทย](README-th.md) | [Türkçe](README-tr.md) | [Tiếng Việt](README-vi.md)
---

## 📖 Table des matières

- [Caractéristiques du projet](#-caractéristiques-du-projet)
- [Architecture du système](#-architecture-du-système)
- [Système de mémoire](#-système-de-mémoire)
- [Navigation intelligente](#-navigation-intelligente)
- [Architecture à double Agent](#-architecture-à-double-agent)
- [Démarrage rapide](#-démarrage-rapide)
- [Déploiement en un clic](#-déploiement-en-un-clic)
- [Fabric Mod API](#-fabric-mod-api)
- [Système Skill DSL](#-système-skill-dsl)
- [Système de sécurité](#-système-de-sécurité)
- [Panneau de contrôle WebUI](#-panneau-de-contrôle-webui)
- [Guide de déploiement](#-guide-de-déploiement)
- [FAQ](#-faq)
- [Feuille de route](#-feuille-de-route)

---

## ✨ Caractéristiques du projet

### 🧠 Système de mémoire — Apprentissage inter-sessions (nouveau en v3.0)

```
Approche traditionnelle : Oublie tout à chaque redémarrage, erreurs répétées, Tokens gaspillés
Approche avec mémoire :  Mémoire à 3 niveaux (espace/chemin/stratégie), JSON persistant, réutilisation inter-sessions
```

- **Mémoire spatiale** : Détecte et mémorise automatiquement les zones de construction protégées, les zones dangereuses et les points de ressources
- **Mémoire de chemin** : Met en cache les chemins réussis, liste noire des chemins échoués, statistiques de taux de réussite
- **Mémoire stratégique** : Les opérations réussies sont automatiquement consolidées en stratégies réutilisables, réutilisées sans coût en Tokens
- **Protection des constructions** : Évite automatiquement les constructions des joueurs lors de la navigation — plus de risque de destruction de base

### 🛤️ Navigation intelligente — Recherche de chemin pilotée par la mémoire (nouveau en v3.0)

```
Approche traditionnelle : walk_to(x,y,z) → Bloqué dans un mur / Traverse une construction
Navigation intelligente : Consulte mémoire → Utilise cache → Baritone (exclut zones protégées) → A* de secours
```

- **Priorité au cache** : Les chemins déjà parcourus sont réutilisés directement, calcul zéro
- **Intégration Baritone** : Le moteur de recherche de chemin communautaire le plus puissant, creuse/ponte/nage automatiquement/évite la lave
- **Injection des zones protégées** : Les constructions mémorisées sont automatiquement injectées comme zones d'exclusion Baritone
- **Apprentissage automatique** : Chaque résultat de navigation est automatiquement enregistré dans le système de mémoire

### 🤖 Architecture à double Agent — Séparation chat et exécution (nouveau en v2.0)

```
Agent principal :   Gère le chat, contexte persistant, uniquement identification d'intentions (~50 Tokens/appel)
Agent d'opération : Gère l'exécution, sans état, contexte neuf (<1500 Tokens/appel)
```

- **Agent principal** : Maintient le contexte de conversation, identifie les balises `[TASK:xxx]`
- **Agent d'opération** : Sans état, utilisé et jeté, évite l'explosion du contexte
- **Injection de mémoire** : Le contexte de mémoire est automatiquement injecté lors des décisions de l'IA (zones protégées, chemins connus, etc.)

### 🔌 Architecture Fabric Mod — Précision et fiabilité

- **Zéro décodage de protocole** : Appel direct des API internes du jeu
- **13 points d'accès HTTP** + événements WebSocket en temps réel
- **Intégration Baritone optionnelle** : Recherche de chemin avancée si disponible, sinon déplacement en ligne droite basique

### 🛡️ Système de sécurité à cinq niveaux

| Niveau | Nom | Exemple | Stratégie |
|--------|-----|---------|-----------|
| 0 | Complètement sûr | Déplacement, saut | Exécution automatique |
| 1 | Faible risque | Creuser de la terre, poser une torche | Exécution automatique |
| 2 | Risque moyen | Miner du minerai, attaquer une créature neutre | Exécution automatique |
| 3 | Haut risque | Allumer de la TNT, verser de la lave | Autorisation du joueur requise |
| 4 | Risque mortel | Placer un bloc de commande | Interdit par défaut |

---

## 🏗️ Architecture du système

```
┌──────────────────────────────────────────────────────────────┐
│                    Serveur Minecraft                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            BlockMind Fabric Mod (Java)                 │  │
│  │                                                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Collecteur│ │Exécuteur │ │Écouteur  │ │Baritone  │ │  │
│  │  │d'état    │ │d'actions │ │d'événmts │ │Moteur de │ │  │
│  │  │Bloc/entt/│ │Déplacer/ │ │Chat/dégâts│ │cheminage │ │  │
│  │  │inv./monde│ │creuser/  │ │chgmt bloc│ │(optionel)│ │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │  │
│  │       └─────────────┼────────────┼────────────┘       │  │
│  │               HTTP API :25580 + WebSocket              │  │
│  └─────────────────────────────┼──────────────────────────┘  │
└────────────────────────────────┼─────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────┐
│                  Backend Python BlockMind                     │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                Architecture à double Agent             │  │
│  │  ┌─────────────────┐  ┌────────────────────────────┐  │  │
│  │  │ Agent principal  │  │ Agent d'opération          │  │  │
│  │  │ (Chat)           │  │ (Exécution, sans état)     │  │  │
│  │  │ Contexte persist.│  │ Contexte neuf à chaque fois│  │  │
│  │  │ Identif. intents │  │ Matching Skill/générer/exé.│  │  │
│  │  └────────┬────────┘  └─────────────┬──────────────┘  │  │
│  └───────────┼─────────────────────────┼─────────────────┘  │
│              │                         │                     │
│  ┌───────────▼─────────────────────────▼─────────────────┐  │
│  │               🧠 Système de mémoire (GameMemory)      │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │ Mémoire  │ │ Mémoire  │ │ Mémoire  │ │ Mémoire  │ │  │
│  │  │ spatiale │ │ de chemin│ │stratégique│ │ du joueur│ │  │
│  │  │Zones prot.│ │Chemins   │ │Stratégies│ │Position  │ │  │
│  │  │Zones dang.│ │réussis   │ │réussies  │ │maison    │ │  │
│  │  │Pts ressce.│ │Blacklist │ │Enregistre│ │Préférences│ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │  │
│  │              JSON persistant (data/memory/)            │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │ Injection                     │
│  ┌──────────┐ ┌──────────────▼──────┐ ┌──────────────────┐  │
│  │Moteur    │ │Navigation intellig. │ │Couche de décision│  │
│  │Skill     │ │Mémoire→cache→Barit. │ │IA                │  │
│  │Pars. DSL │ │→A*→auto-apprentiss. │ │Injection contexte│  │
│  │Match/Exé.│ │                     │ │provider.py       │  │
│  └──────────┘ └─────────────────────┘ └──────────────────┘  │
│  ┌──────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │Vérif.   │ │Santé/monitor │ │ WebUI (Miuix Console)   │ │
│  │sécurité │ │3 niveaux     │ │ Thème sombre/config mod.│ │
│  │5 niveaux│ │dégradation   │ │                         │ │
│  └──────────┘ └──────────────┘ └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Exemple de flux de données

**Navigation intelligente pilotée par la mémoire :**
```
Le joueur dit "Rentrer chez moi"
  → L'agent principal identifie la tâche [TASK:rentrer_maison]
  → Agent d'opération correspond au Skill go_home
  → SmartNavigator interroge la mémoire :
      ✅ Position maison : (65, 64, -120) provenant de la mémoire joueur
      ✅ Chemin en cache : parcouru 3 fois, taux de réussite 100%
      ✅ Zone protégée : 30 blocs autour de la base, destruction interdite
      ✅ Zone dangereuse : (80,12,-50) présence de lave
  → Navigation Baritone :
      GoalBlock(65, 64, -120)
      + exclusion_zones=[zone protégée base]
      → Détournement automatique, aucune construction détruite
  → Arrivée : chemin en cache success_count+1
  → Prochaine navigation : utilise directement le chemin en cache, zéro consommation de Tokens
```

---

## 🧠 Système de mémoire

### Architecture de mémoire à trois niveaux

| Niveau | Contenu stocké | Persistant | Exemple |
|--------|---------------|------------|---------|
| **Mémoire spatiale** | Zones protégées, zones dangereuses, points de ressources, base | ✅ JSON | "Base : (50-100, 60-80, -150--90)" |
| **Mémoire de chemin** | Cache de chemins réussis, blacklist de chemins échoués, taux de réussite | ✅ JSON | "Maison→Mine : via (70,64,-100) taux réussite 100%" |
| **Mémoire stratégique** | Consolidation de stratégies réussies, leçons d'échec, balises de contexte | ✅ JSON | "En minant, poser la torche avant de creuser, efficacité maximale" |
| **Mémoire joueur** | Position maison, outils préférés, historique d'interactions | ✅ JSON | "La maison de Steve est à (100,64,200)" |
| **Mémoire monde** | Point d'apparition, points sûrs, événements importants | ✅ JSON | "Point d'apparition (0,64,0), liste des points sûrs" |

### Protection automatique des constructions

```python
# Enregistrer une zone de construction protégée (interdiction de destruction par l'IA)
memory.register_building("Ville principale", center=(100, 64, 200), radius=30)
# → Injecté automatiquement comme exclusion_zones dans Baritone lors de la navigation
# → type : "no_break" + "no_place"
# → L'IA ne peut pas déposer/poser de blocs dans la zone protégée

# Détection automatique (scan environnant toutes les 60 secondes)
navigator.auto_detect_and_memorize()
# → Blocs de construction consécutifs détectés → enregistrés automatiquement comme zone protégée
# → Lave/flamme détectée → enregistrée automatiquement comme zone dangereuse
# → Concentration de minerais détectée → enregistrée automatiquement comme point de ressources
```

### Mécanisme de cache de chemins

```python
# Première navigation : planification IA + exécution
result = await navigator.goto(100, 64, 200)
# → Chemin mis en cache : success_count=1, success_rate=100%

# Deuxième navigation : utilise directement le cache
result = await navigator.goto(100, 64, 200)
# → Cache de chemin atteint, exécution directe, calcul zéro

# Chemins échoués : apprentissage automatique
# → fail_count >= 3 → ajouté automatiquement à la blacklist
# → Replanification la prochaine fois, ancien chemin non réutilisé
```

### Consolidation automatique des stratégies

```python
# Enregistrement automatique après exécution réussie de l'Agent d'opération
memory.record_strategy(
    task_type="mine",
    description="Poser la torche avant de miner",
    action_sequence=[...],
    success=True,
    context_tags=["nighttime", "cave"],
)

# Correspondance automatique de la meilleure stratégie pour le même type de tâche
best = memory.get_best_strategy("mine", context_tags=["nighttime"])
# → Retourne la stratégie avec le taux de réussite le plus élevé
```

### Injection du contexte de mémoire dans l'IA

```python
# Injection automatique de la mémoire à chaque décision de l'IA
memory_context = memory.get_ai_context()
# Sortie :
# [Système de mémoire]
# Base :
#   - Maison : (50, 64, -100) (rayon 30)
# Zones protégées (destruction interdite) :
#   - Ville principale : (100, 64, 200) (rayon 20)
# Zones dangereuses :
#   - Lac de lave : (80, 12, -50) (lave)
# Chemins fiables connus : 3
# Stratégies vérifiées : 5
```

---

## 🛤️ Navigation intelligente

### Flux de navigation

```
SmartNavigator.goto(x, y, z)
  │
  ├── 1. Vérification de sécurité
  │     └── Cible dans une zone protégée ? → Alerte mais pas de rejet
  │
  ├── 2. Consultation du cache de chemins
  │     └── Cache fiable disponible ? → Exécution directe du chemin en cache
  │
  ├── 3. Obtention du contexte de navigation
  │     ├── Zones exclues (zones protégées)
  │     ├── Zones dangereuses (lave, falaises)
  │     └── Référence de chemins fiables
  │
  ├── 4. Recherche de chemin Baritone (prioritaire)
  │     ├── Injection des exclusion_zones
  │     ├── Creusage / pont / nage automatiques
  │     └── Coût de chute / évitement de lave
  │
  ├── 5. Recherche de chemin A* (secours)
  │     └── A* sur grille basique + vérification de passabilité des blocs
  │
  └── 6. Enregistrement du résultat
        ├── Succès → cache_path(success=True)
        └── Échec → cache_path(success=False) + possible blacklist
```

### Intégration Baritone

| Fonctionnalité | Baritone | A* basique |
|----------------|----------|------------|
| Algorithme de chemin | A* amélioré + heuristique de coût | A* standard |
| Creusage | ✅ Traverse automatiquement les obstacles | ❌ |
| Construction de pont | ✅ Mode scaffold | ❌ |
| Natation | ✅ | ❌ |
| Déplacement vertical | ✅ Saut/échelle/lierre | ⚠️ 1 bloc seulement |
| Évitement de lave | ✅ Pénalité de coût | ❌ |
| Coût de chute | ✅ Intégré dans l'heuristique | ❌ |
| Zones d'exclusion | ✅ `exclusionAreas` | ❌ |
| **Protection des constructions** | ✅ Injection de zones `no_break` | ❌ |

### Types de zones d'exclusion

| Type | Description | Source |
|------|-------------|--------|
| `no_break` | Destruction de blocs interdite | Zones protégées, base |
| `no_place` | Placement de blocs interdit | Zones protégées |
| `avoid` | Contournement complet | Zones dangereuses (lave, etc.) |

---

## 🤖 Architecture à double Agent

### Pourquoi un double Agent ?

```
Problème de l'agent unique :
  Contexte chat + contexte opération → Explosion de Tokens (>4000/appel)
  Échec d'opération pollue le chat → Mauvaise expérience de conversation
  Chaque opération transporte l'historique complet du chat → Gaspillage

Solution double Agent :
  Agent principal : chat uniquement, fenêtre glissante de 20 messages, ~50 Tokens/appel
  Agent d'opération : sans état, contexte neuf, <1500 Tokens/appel
```

### Flux

```
Message du joueur
  → Agent principal chat (contexte persistant)
  → Balise [TASK:xxx] identifiée
  → Description de tâche extraite
  → Agent d'opération exécute (sans état) :
      ├── Recherche de correspondance Skill
      ├── Injection du contexte mémoire
      ├── L1/L2 : Exécution du Skill en cache
      ├── L3 : IA remplit le modèle + exécution
      └── L4 : Raisonnement IA complet + exécution
  → Agent principal formate la réponse → Joueur
```

---
## 🚀 Démarrage rapide

### Prérequis

| Composant | Version requise |
|-----------|-----------------|
| Python | 3.10+ |
| Java | 17+ |
| Minecraft | 1.19.4 - 1.21.4 |
| Fabric Loader | 0.15+ |

---

## 📦 Déploiement en un clic

### Téléchargement

Télécharger depuis [GitHub Releases](https://github.com/bmbxwbh/BlockMind/releases/latest) :

| Fichier | Description |
|---------|-------------|
| `blockmind-mod-1.0.0.jar` | Fabric Mod (à placer dans mods/ du serveur) |
| `Source code` (zip/tar) | Code source complet |

### Démarrage en un clic — Linux / macOS

```bash
# Cloner
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

# Démarrage en un clic (installation auto des dépendances + serveur MC + BlockMind + WebUI)
chmod +x start.sh
./start.sh
```

> `start.sh` automatise : détection Python/Java → installation des dépendances → scan du serveur MC existant → sélection de version et installation → démarrage complet

### Démarrage en un clic — Windows

```cmd
:: Cloner (ou télécharger le zip et extraire)
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

:: Installation en un clic
install.bat

:: Démarrage en un clic (serveur MC + BlockMind + WebUI)
start_all.bat
```

> Étapes détaillées dans le [Guide de déploiement Windows](docs/WINDOWS.md)

### Déploiement Docker

```bash
# Télécharger l'image
docker pull ghcr.io/bmbxwbh/blockmind:latest

# Télécharger le modèle de configuration
wget https://raw.githubusercontent.com/bmbxwbh/BlockMind/main/config.example.yaml -O config.yaml
# Éditer config.yaml avec la configuration de votre modèle IA

# Démarrer
docker run -d \
  --name blockmind \
  -p 19951:19951 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v blockmind-data:/data \
  ghcr.io/bmbxwbh/blockmind:latest
```

Ou avec docker-compose :

```bash
git clone https://github.com/bmbxwbh/BlockMind.git && cd BlockMind
cp config.example.yaml config.yaml
# Éditer config.yaml
docker compose up -d
```

```bash
# Consulter les logs
docker compose logs -f blockmind
# Arrêter
docker compose down
```

### Configuration

Éditer `config.yaml` :

```yaml
ai:
  main_agent:
    provider: "openai"          # openai ou anthropic
    api_key: "sk-your-key"
    model: "gpt-4o"             # Nom de votre modèle
    base_url: ""                # URL d'API personnalisée (optionnel)

webui:
  enabled: true
  port: 19951
  auth:
    password: "your-password"   # Mot de passe de connexion WebUI
```

Après le démarrage, accédez à `http://localhost:19951` pour ouvrir le panneau de contrôle.

---

## 🔌 Fabric Mod API

### Requêtes d'état

| Point d'accès | Méthode | Description |
|---------------|---------|-------------|
| `/health` | GET | Vérification de santé |
| `/api/status` | GET | État du joueur |
| `/api/world` | GET | État du monde |
| `/api/inventory` | GET | Informations d'inventaire |
| `/api/entities?radius=32` | GET | Entités à proximité |
| `/api/blocks?radius=16` | GET | Blocs à proximité |

### Exécution d'actions

| Point d'accès | Méthode | Description |
|---------------|---------|-------------|
| `/api/move` | POST | Déplacer vers les coordonnées |
| `/api/dig` | POST | Creuser un bloc |
| `/api/place` | POST | Placer un bloc |
| `/api/attack` | POST | Attaquer une entité |
| `/api/eat` | POST | Manger |
| `/api/look` | POST | Regarder vers les coordonnées |
| `/api/chat` | POST | Envoyer un message |

### Planification de chemin

| Point d'accès | Méthode | Description |
|---------------|---------|-------------|
| `/api/pathfind` | POST | Navigation par chemin (Baritone/A*) |
| `/api/pathfind/stop` | POST | Arrêter la navigation |
| `/api/pathfind/status` | GET | État de la navigation |

### Événements diffusés

Le Mod diffuse des événements via WebSocket :
- `player_damaged` — Joueur blessé
- `entity_attack` — Attaqué
- `health_low` — Points de vie faibles
- `inventory_full` — Inventaire plein
- `block_broken` — Bloc creusé

---

## 📝 Système Skill DSL

### Classification des tâches

| Niveau | Type | Exemple | Stratégie de cache |
|--------|------|---------|-------------------|
| L1 | Tâche fixe | "Rentrer chez moi" | Exécution directe |
| L2 | Tâche paramétrée | "Miner 10 diamants" | Cache avec paramètres |
| L3 | Tâche par modèle | "Construire un abri" | Correspondance de modèle |
| L4 | Tâche dynamique | "Aide-moi à vaincre l'Ender Dragon" | Raisonnement IA |

### Exemple de Skill YAML

```yaml
skill_id: mine_diamonds
name: "Miner des diamants"
level: L2
parameters:
  count: {type: int, default: 10, min: 1, max: 64}
steps:
  - action: pathfind
    target: {y: -59}
    note: "Se rendre à la couche de diamants"
  - action: dig_loop
    block: diamond_ore
    count: ${count}
  - action: pathfind
    target: home
    note: "Retour à la base"
```

---

## 🛡️ Système de sécurité

| Niveau | Mécanisme | Description |
|--------|-----------|-------------|
| L1 | Évaluation des risques | Chaque action notée de 0 à 100 |
| L2 | Autorisation d'opération | Confirmation requise pour les hauts risques |
| L3 | Prise de contrôle d'urgence | Le joueur peut interrompre l'IA à tout moment |
| L4 | Journal d'audit | Toutes les opérations sont traçables |
| L5 | Restriction de zone sûre | Limite la portée de destruction/placement |

---

## 🖥️ Panneau de contrôle WebUI

Après le démarrage, accédez à `http://localhost:19951`. Prise en charge de :

- 📊 Tableau de bord — Surveillance de l'état en temps réel
- 🛠️ Gestion des Skills — Édition YAML en ligne
- 🧠 Système de mémoire — Consultation/nettoyage/sauvegarde
- 🤖 Configuration du modèle — Basculement à chaud du modèle IA
- 💬 Panneau de commandes — Instructions en langage naturel
- 📋 File d'attente des tâches — Consultation de l'état d'exécution
- 📝 Centre de logs — Flux de logs en temps réel

---

## ❓ FAQ

**Q : Baritone est-il obligatoire ?**
R : Non. Baritone est une dépendance optionnelle. Sans lui, le système revient automatiquement au déplacement en ligne droite basique avec A*.

**Q : Où sont stockées les données de mémoire ?**
R : Dans le répertoire `data/memory/`, sous forme de 5 fichiers JSON, conservés entre les sessions.

**Q : Comment la protection des constructions fonctionne-t-elle ?**
R : Deux façons : ① enregistrement manuel ② détection automatique (scan toutes les 60 secondes).

**Q : Quels fournisseurs IA sont supportés ?**
R : Format compatible OpenAI (incluant DeepSeek/OpenRouter/MiMo, etc.) + format Anthropic.

**Q : Quelle est la taille de l'image Docker ?**
R : Environ 200 Mo, basée sur python:3.11-slim avec construction multi-étapes.

---

## 🗺️ Feuille de route

### v3.0 (actuel) ✅
- [x] Système de mémoire à trois niveaux (espace/chemin/stratégie)
- [x] Navigation intelligente (pilotée par mémoire + intégration Baritone)
- [x] Architecture à double Agent (séparation chat/exécution)
- [x] Protection automatique des zones de construction
- [x] WebUI Miuix Console
- [x] Déploiement en un clic Windows/Linux
- [x] Image Docker + publication automatique GHCR
- [x] CI/CD GitHub Actions

### v3.1 (prévu)
- [ ] Entrées multimodales (analyse de captures d'écran)
- [ ] Marketplace de Skills (import/export)
- [ ] Collaboration multijoueur
- [ ] Interaction vocale

---

## 📄 Licence

MIT License. Voir [LICENSE](LICENSE) pour les détails.
