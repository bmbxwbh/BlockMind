# 🧠 BlockMind — Sistema de Compañero Inteligente para Minecraft

> **Fabric Mod + Impulsado por IA + Sistema de Memoria** · v3.0 · 2026-04-30

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![Fabric](https://img.shields.io/badge/Fabric-0.92+-yellow.svg)](https://fabricmc.net)
[![MC](https://img.shields.io/badge/Minecraft-1.20.x--1.21.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**Resumen en una frase:** Fabric Mod proporciona interfaces precisas del juego + Backend en Python impulsa la toma de decisiones de IA + Sistema de memoria para aprendizaje entre sesiones, logrando un compañero inteligente de Minecraft con supervivencia autónoma 7×24.

🌐 [中文](README.md) | [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | **Español** | [Français](README-fr.md) | [Bahasa Indonesia](README-id.md) | [Italiano](README-it.md) | [Português](README-pt.md) | [Русский](README-ru.md) | [ภาษาไทย](README-th.md) | [Türkçe](README-tr.md) | [Tiếng Việt](README-vi.md)
---

## 📖 Índice

- [Características del proyecto](#-características-del-proyecto)
- [Arquitectura del sistema](#-arquitectura-del-sistema)
- [Sistema de memoria](#-sistema-de-memoria)
- [Navegación inteligente](#-navegación-inteligente)
- [Arquitectura de doble Agente](#-arquitectura-de-doble-agente)
- [Inicio rápido](#-inicio-rápido)
- [Despliegue con un clic](#-despliegue-con-un-clic)
- [API del Fabric Mod](#-api-del-fabric-mod)
- [Sistema Skill DSL](#-sistema-skill-dsl)
- [Sistema de seguridad](#-sistema-de-seguridad)
- [Panel de control WebUI](#-panel-de-control-webui)
- [Guía de despliegue](#-guía-de-despliegue)
- [FAQ](#-faq)
- [Hoja de ruta](#-hoja-de-ruta)

---

## ✨ Características del proyecto

### 🧠 Sistema de memoria — Aprendizaje entre sesiones (nuevo en v3.0)

```
Método tradicional:  Olvida todo al reiniciar, comete los mismos errores, consume Tokens repetidamente
Con memoria:         Tres capas de memoria (espacial/ruta/estrategia), JSON persistente, reutilización entre sesiones
```

- **Memoria espacial**: Detecta y recuerda automáticamente zonas protegidas de construcción, áreas peligrosas y puntos de recursos
- **Memoria de rutas**: Cacha rutas exitosas, lista negra de rutas fallidas, estadísticas de tasa de éxito
- **Memoria de estrategias**: Las operaciones exitosas se consolidan automáticamente como estrategias reutilizables, reutilización con cero Tokens
- **Protección de construcciones**: Evita automáticamente las construcciones de los jugadores al navegar, sin más riesgo de destruir hogares

### 🛤️ Navegación inteligente — Búsqueda de caminos impulsada por memoria (nuevo en v3.0)

```
Método tradicional:  walk_to(x,y,z) → Se atasca contra muros / Destruye construcciones
Navegación inteligente: Consultar memoria → Usar caché → Baritone(excluir zonas protegidas) → Respaldo A*
```

- **Prioridad de caché**: Los caminos recorridos se reutilizan directamente, sin cálculo
- **Integración con Baritone**: El motor de búsqueda de caminos más potente de la comunidad, excava/puentes/nado/evita lava automáticamente
- **Inyección de zonas protegidas**: Las construcciones en memoria se inyectan automáticamente como zonas de exclusión de Baritone
- **Aprendizaje automático**: Cada resultado de navegación se registra automáticamente en el sistema de memoria

### 🤖 Arquitectura de doble Agente — Aislamiento entre chat y operaciones (nuevo en v2.0)

```
Agente principal:    Responsable del chat, contexto persistente, solo identificación de intención (~50 Tokens/vez)
Agente de operaciones: Responsable de ejecución, sin estado, contexto nuevo (<1500 Tokens/vez)
```

- **Agente principal**: Mantiene el contexto de la conversación, identifica etiquetas `[TASK:xxx]`
- **Agente de operaciones**: Sin estado, se descarta tras usar, evita la explosión de contexto
- **Inyección de memoria**: El contexto de memoria se inyecta automáticamente durante las decisiones de IA (zonas protegidas, rutas conocidas, etc.)

### 🔌 Arquitectura del Fabric Mod — Precisa y confiable

- **Cero análisis de protocolo**: Llamada directa a la API interna del juego
- **13 endpoints HTTP** + WebSocket para eventos en tiempo real
- **Integración opcional con Baritone**: Con él, búsqueda de caminos avanzada; sin él, movimiento lineal básico

### 🛡️ Sistema de seguridad de cinco niveles

| Nivel | Nombre | Ejemplo | Estrategia |
|------|------|------|------|
| 0 | Completamente seguro | Mover, saltar | Ejecución automática |
| 1 | Bajo riesgo | Excavar tierra, colocar antorchas | Ejecución automática |
| 2 | Riesgo medio | Excavar minerales, atacar criaturas neutrales | Ejecución automática |
| 3 | Alto riesgo | Encender TNT, colocar lava | Requiere autorización del jugador |
| 4 | Riesgo letal | Colocar bloque de comandos | Prohibido por defecto |

---

## 🏗️ Arquitectura del sistema

```
┌──────────────────────────────────────────────────────────────┐
│                    Servidor Minecraft                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            BlockMind Fabric Mod (Java)                 │  │
│  │                                                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Recolector│ │Ejecutor  │ │Escucha-  │ │Baritone  │ │  │
│  │  │de estado │ │de accio- │ │dor de    │ │Motor de  │ │  │
│  │  │bloque/   │ │nes: mover│ │eventos:  │ │búsqueda  │ │  │
│  │  │entidad/  │ │excavar/  │ │chat/daño/│ │de caminos│ │  │
│  │  │inventario│ │colocar/  │ │cambio de │ │(opcional)│ │  │
│  │  │/mundo    │ │atacar    │ │bloques   │ │          │ │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │  │
│  │       └─────────────┼────────────┼────────────┘       │  │
│  │               HTTP API :25580 + WebSocket              │  │
│  └─────────────────────────────┼──────────────────────────┘  │
└────────────────────────────────┼─────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────┐
│                  Backend Python de BlockMind                  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            Arquitectura de doble Agente               │  │
│  │  ┌─────────────────┐  ┌────────────────────────────┐  │  │
│  │  │ Agente principal│  │ Agente de operaciones      │  │  │
│  │  │ (Chat)          │  │ (Ejecución, sin estado)    │  │  │
│  │  │ Contexto persis-│  │ Contexto nuevo cada vez    │  │  │
│  │  │ tente           │  │ Match/Ejecución de Skills  │  │  │
│  │  │ Identificación  │  │                            │  │  │
│  │  │ de intención    │  │                            │  │  │
│  │  └────────┬────────┘  └─────────────┬──────────────┘  │  │
│  └───────────┼─────────────────────────┼─────────────────┘  │
│              │                         │                     │
│  ┌───────────▼─────────────────────────▼─────────────────┐  │
│  │               🧠 Sistema de Memoria (GameMemory)       │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Memoria   │ │Memoria de│ │Memoria de│ │Memoria   │ │  │
│  │  │espacial  │ │rutas     │ │estrategias│ │del jugador│ │  │
│  │  │Zonas pro-│ │Rutas     │ │Estrategias│ │Ubicación │ │  │
│  │  │tegidas   │ │exitosas  │ │exitosas  │ │del hogar │ │  │
│  │  │Áreas     │ │Lista     │ │Registro  │ │Preferen- │ │  │
│  │  │peligrosas│ │negra de  │ │de fallos │ │cias de   │ │  │
│  │  │Recursos  │ │fallos    │ │Etiquetas │ │herramien-│ │  │
│  │  │minerales │ │Estad. de │ │de contex-│ │tas       │ │  │
│  │  │          │ │éxito     │ │to        │ │Registro  │ │  │
│  │  │          │ │          │ │          │ │interacción│ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │  │
│  │              JSON persistente (data/memory/)            │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │ Inyección                     │
│  ┌──────────┐ ┌──────────────▼──────┐ ┌──────────────────┐  │
│  │Motor de  │ │Navegación          │ │Capa de decisión  │  │
│  │Skills    │ │inteligente         │ │de IA             │  │
│  │Análisis  │ │Memoria→Caché→      │ │Inyección de      │  │
│  │DSL       │ │Baritone→Respaldo   │ │contexto de       │  │
│  │Match/    │ │A*→Auto-aprendizaje │ │memoria           │  │
│  │Ejecución │ │                    │ │provider.py       │  │
│  └──────────┘ └─────────────────────┘ └──────────────────┘  │
│  ┌──────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │Verifica- │ │Monitoreo de  │ │ WebUI (Miuix Console)   │ │
│  │ción de   │ │salud         │ │ Tema oscuro/Config. de  │ │
│  │seguridad │ │Degradación   │ │ modelos                 │ │
│  │5 niveles │ │3 niveles     │ │                         │ │
│  └──────────┘ └──────────────┘ └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Ejemplo de flujo de datos

**Navegación inteligente impulsada por memoria:**
```
El jugador dice "ir a casa"
  → Agente principal identifica la tarea [TASK:ir a casa]
  → Agente de operaciones hace match con el Skill go_home
  → SmartNavigator consulta la memoria:
      ✅ Ubicación del hogar: (65, 64, -120) de la memoria del jugador
      ✅ Ruta en caché: Recorrida 3 veces, tasa de éxito 100%
      ✅ Zona protegida: Radio de 30 bloques alrededor de la base, destrucción prohibida
      ✅ Área peligrosa: (80,12,-50) hay lava
  → Navegación con Baritone:
      GoalBlock(65, 64, -120)
      + exclusion_zones=[zona protegida de la base]
      → Desvío automático, sin destruir ninguna construcción
  → Al llegar: Caché de ruta success_count+1
  → La próxima vez: Usa directamente la ruta en caché, consumo cero de Tokens
```

---

## 🧠 Sistema de memoria

### Arquitectura de tres capas de memoria

| Capa | Contenido almacenado | Persistencia | Ejemplo |
|---|---------|--------|------|
| **Memoria espacial** | Zonas protegidas, áreas peligrosas, puntos de recursos, base | ✅ JSON | "Rango de la base: (50-100, 60-80, -150--90)" |
| **Memoria de rutas** | Caché de rutas exitosas, lista negra de rutas fallidas, tasa de éxito | ✅ JSON | "Cueva→Mina: Pasando por (70,64,-100) tasa de éxito 100%" |
| **Memoria de estrategias** | Consolidación de estrategias exitosas, lecciones de fallos, etiquetas de contexto | ✅ JSON | "Al minar, colocar antorcha primero y luego excavar, máxima eficiencia" |
| **Memoria del jugador** | Ubicación del hogar, herramientas preferidas, registro de interacciones | ✅ JSON | "El hogar de Steve está en (100,64,200)" |
| **Memoria del mundo** | Punto de spawn, puntos seguros, eventos importantes | ✅ JSON | "Punto de spawn (0,64,0), lista de puntos seguros" |

### Protección automática de construcciones

```python
# Registrar zona protegida de construcción (prohibir que la IA la destruya)
memory.register_building("Ciudad principal", center=(100, 64, 200), radius=30)
# → Se inyecta automáticamente como exclusion_zones de Baritone al navegar
# → type: "no_break" + "no_place"
# → La IA no puede destruir/colocar bloques dentro de la zona protegida

# Detección automática (escaneo del entorno cada 60 segundos)
navigator.auto_detect_and_memorize()
# → Detecta bloques de construcción continuos → Registra automáticamente como zona protegida
# → Detecta lava/fuego → Registra automáticamente como área peligrosa
# → Detecta acumulación de minerales → Registra automáticamente como punto de recursos
```

### Mecanismo de caché de rutas

```python
# Primera navegación: Planificación y ejecución de IA
result = await navigator.goto(100, 64, 200)
# → Ruta en caché: success_count=1, success_rate=100%

# Segunda navegación: Usa directamente el caché
result = await navigator.goto(100, 64, 200)
# → Acierto en caché de ruta, ejecución directa, cero cálculo

# Rutas fallidas: Aprendizaje automático
# → fail_count >= 3 → Se añade automáticamente a la lista negra
# → La próxima vez replanifica, no usa la ruta anterior
```

### Consolidación automática de estrategias

```python
# Registro automático tras ejecución exitosa del Agente de operaciones
memory.record_strategy(
    task_type="mine",
    description="Colocar antorcha primero y luego minar",
    action_sequence=[...],
    success=True,
    context_tags=["nighttime", "cave"],
)

# La próxima vez hace match automáticamente con la mejor estrategia para el mismo tipo de tarea
best = memory.get_best_strategy("mine", context_tags=["nighttime"])
# → Devuelve la estrategia con mayor tasa de éxito
```

### Inyección de contexto de memoria en la IA

```python
# Inyección automática de memoria en cada decisión de IA
memory_context = memory.get_ai_context()
# Salida:
# [Sistema de memoria]
# Base:
#   - Hogar: (50, 64, -100) (radio 30)
# Zonas protegidas (destrucción prohibida):
#   - Ciudad principal: (100, 64, 200) (radio 20)
# Áreas peligrosas:
#   - Lago de lava: (80, 12, -50) (lava)
# Rutas confiables conocidas: 3
# Estrategias verificadas: 5
```

---

## 🛤️ Navegación inteligente

### Flujo de navegación

```
SmartNavigator.goto(x, y, z)
  │
  ├── 1. Verificación de seguridad
  │     └── ¿El destino está en zona protegida? → Advertir pero no rechazar
  │
  ├── 2. Consulta de caché de rutas
  │     └── ¿Hay caché confiable? → Ejecutar directamente la ruta en caché
  │
  ├── 3. Obtener contexto de navegación
  │     ├── Zonas de exclusión (zonas protegidas de construcción)
  │     ├── Áreas peligrosas (lava, acantilados)
  │     └── Referencias de rutas confiables
  │
  ├── 4. Búsqueda de caminos con Baritone (prioritario)
  │     ├── Inyección de exclusion_zones
  │     ├── Excavar/puentes/nado automáticos
  │     └── Costo de caída / Evitar lava
  │
  ├── 5. Búsqueda de caminos con A* (respaldo)
  │     └── A* de cuadrícula básica + verificación de transitabilidad
  │
  └── 6. Registro de resultado
        ├── Éxito → cache_path(success=True)
        └── Fallo → cache_path(success=False) + Posible lista negra
```

### Integración con Baritone

| Característica | Baritone | A* básico |
|------|----------|---------|
| Algoritmo | A* mejorado + heurística de costo | A* estándar |
| Excavar | ✅ Excava automáticamente a través de obstáculos | ❌ |
| Puentes | ✅ Modo scaffold | ❌ |
| Nado | ✅ | ❌ |
| Movimiento vertical | ✅ Salto/escalera/enredadera | ⚠️ Solo 1 bloque |
| Evitar lava | ✅ Penalización de costo | ❌ |
| Costo de caída | ✅ Incluido en la heurística | ❌ |
| Zonas de exclusión | ✅ `exclusionAreas` | ❌ |
| **Protección de construcciones** | ✅ Inyección de zonas `no_break` | ❌ |

### Tipos de zonas de exclusión

| Tipo | Descripción | Origen |
|------|------|------|
| `no_break` | Prohibir destruir bloques | Zonas protegidas de construcción, base |
| `no_place` | Prohibir colocar bloques | Zonas protegidas de construcción |
| `avoid` | Evitar completamente | Áreas peligrosas (lava, etc.) |

---

## 🤖 Arquitectura de doble Agente

### ¿Por qué se necesita doble Agente?

```
Problema con un solo Agente:
  Contexto de chat + Contexto de operación → Explosión de Tokens (>4000/vez)
  Fallo de operación contamina el chat → Mala experiencia de conversación
  Cada operación lleva el historial completo del chat → Desperdicio

Solución de doble Agente:
  Agente principal: Solo chat, ventana deslizante de 20 mensajes, ~50 Tokens/vez
  Agente de operaciones: Sin estado, contexto nuevo, <1500 Tokens/vez
```

### Flujo

```
Mensaje del jugador
  → Agente principal (chat, contexto persistente)
  → Detecta etiqueta [TASK:xxx]
  → Extrae descripción de la tarea
  → Agente de operaciones ejecuta (sin estado):
      ├── Match de Skill
      ├── Inyección de contexto de memoria
      ├── L1/L2: Ejecutar Skill en caché
      ├── L3: IA rellena plantilla + ejecuta
      └── L4: IA razona completamente + ejecuta
  → Agente principal formatea respuesta → Jugador
```

---
## 🚀 Inicio rápido

### Requisitos del entorno

| Componente | Requisito |
|------|------|
| Python | 3.10+ |
| Java | 17+ |
| Minecraft | 1.19.4 - 1.21.4 |
| Fabric Loader | 0.15+ |

---

## 📦 Despliegue con un clic

### Descarga

Descargar desde [GitHub Releases](https://github.com/bmbxwbh/BlockMind/releases/latest):

| Archivo | Descripción |
|------|------|
| `blockmind-mod-1.0.0.jar` | Fabric Mod (colocar en mods/ del servidor) |
| `Source code` (zip/tar) | Código fuente completo |

### Inicio con un clic en Linux / macOS

```bash
# Clonar
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

# Inicio con un clic (instala dependencias automáticamente + Servidor MC + BlockMind + WebUI)
chmod +x start.sh
./start.sh
```

> `start.sh` automáticamente: Detecta Python/Java → Instala dependencias → Escanea servidores MC existentes → Selecciona e instala versión → Inicia todo

### Inicio con un clic en Windows

```cmd
:: Clonar (o descargar zip y descomprimir)
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

:: Instalación con un clic
install.bat

:: Inicio con un clic (Servidor MC + BlockMind + WebUI)
start_all.bat
```

> Consulta los pasos detallados en la [Guía de despliegue para Windows](docs/WINDOWS.md)

### Despliegue con Docker

```bash
# Descargar imagen
docker pull ghcr.io/bmbxwbh/blockmind:latest

# Descargar plantilla de configuración
wget https://raw.githubusercontent.com/bmbxwbh/BlockMind/main/config.example.yaml -O config.yaml
# Editar config.yaml con la configuración de tu modelo de IA

# Iniciar
docker run -d \
  --name blockmind \
  -p 19951:19951 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v blockmind-data:/data \
  ghcr.io/bmbxwbh/blockmind:latest
```

O usar docker-compose:

```bash
git clone https://github.com/bmbxwbh/BlockMind.git && cd BlockMind
cp config.example.yaml config.yaml
# Editar config.yaml
docker compose up -d
```

```bash
# Ver registros
docker compose logs -f blockmind
# Detener
docker compose down
```

### Configuración

Editar `config.yaml`:

```yaml
ai:
  main_agent:
    provider: "openai"          # openai o anthropic
    api_key: "sk-your-key"
    model: "gpt-4o"             # Nombre de tu modelo
    base_url: ""                # URL personalizada de API (opcional)

webui:
  enabled: true
  port: 19951
  auth:
    password: "your-password"   # Contraseña de inicio de sesión del WebUI
```

Tras iniciar, accede a `http://localhost:19951` para entrar al panel de control.

---

## 🔌 API del Fabric Mod

### Consulta de estado

| Endpoint | Método | Descripción |
|------|------|------|
| `/health` | GET | Verificación de salud |
| `/api/status` | GET | Estado del jugador |
| `/api/world` | GET | Estado del mundo |
| `/api/inventory` | GET | Información del inventario |
| `/api/entities?radius=32` | GET | Entidades cercanas |
| `/api/blocks?radius=16` | GET | Bloques cercanos |

### Ejecución de acciones

| Endpoint | Método | Descripción |
|------|------|------|
| `/api/move` | POST | Mover a coordenadas |
| `/api/dig` | POST | Excavar bloque |
| `/api/place` | POST | Colocar bloque |
| `/api/attack` | POST | Atacar entidad |
| `/api/eat` | POST | Comer |
| `/api/look` | POST | Mirar hacia coordenadas |
| `/api/chat` | POST | Enviar mensaje de chat |

### Planificación de rutas

| Endpoint | Método | Descripción |
|------|------|------|
| `/api/pathfind` | POST | Navegación por ruta (Baritone/A*) |
| `/api/pathfind/stop` | POST | Detener navegación |
| `/api/pathfind/status` | GET | Estado de navegación |

### Envío de eventos

El Mod envía eventos a través de WebSocket:
- `player_damaged` — Jugador herido
- `entity_attack` — Atacado
- `health_low` — Vida baja
- `inventory_full` — Inventario lleno
- `block_broken` — Excavación de bloque completada

---

## 📝 Sistema Skill DSL

### Clasificación de tareas

| Nivel | Tipo | Ejemplo | Estrategia de caché |
|------|------|------|----------|
| L1 | Tarea fija | "Ir a casa" | Ejecución directa |
| L2 | Tarea parametrizada | "Excavar 10 diamantes" | Caché con parámetros |
| L3 | Tarea de plantilla | "Construir un refugio" | Match de plantilla |
| L4 | Tarea dinámica | "Ayúdame a vencer al Ender Dragon" | Razonamiento de IA |

### Ejemplo de Skill YAML

```yaml
skill_id: mine_diamonds
name: "Excavar diamantes"
level: L2
parameters:
  count: {type: int, default: 10, min: 1, max: 64}
steps:
  - action: pathfind
    target: {y: -59}
    note: "Ir a la capa de diamantes"
  - action: dig_loop
    block: diamond_ore
    count: ${count}
  - action: pathfind
    target: home
    note: "Volver a la base"
```

---

## 🛡️ Sistema de seguridad

| Nivel | Mecanismo | Descripción |
|------|------|------|
| L1 | Evaluación de riesgo | Cada acción se puntúa de 0 a 100 |
| L2 | Autorización de operaciones | Las de alto riesgo requieren confirmación |
| L3 | Control de emergencia | El jugador puede interrumpir la IA en cualquier momento |
| L4 | Registro de auditoría | Todas las operaciones son rastreables |
| L5 | Restricción de zona segura | Limita el rango de destrucción/colocación |

---

## 🖥️ Panel de control WebUI

Tras iniciar, accede a `http://localhost:19951`, soporta:

- 📊 Panel de control — Monitoreo de estado en tiempo real
- 🛠️ Gestión de Skills — Edición en línea de YAML
- 🧠 Sistema de memoria — Ver/Limpiar/Respaldar
- 🤖 Configuración de modelos — Cambio en caliente de modelos de IA
- 💬 Panel de comandos — Instrucciones en lenguaje natural
- 📋 Cola de tareas — Ver estado de ejecución
- 📝 Centro de registros — Flujo de registros en tiempo real

---

## ❓ FAQ

**¿Es obligatorio instalar Baritone?**
No. Baritone es una dependencia opcional. Sin él, se recurre automáticamente al movimiento lineal básico con A*.

**¿Dónde se almacenan los datos de memoria?**
En el directorio `data/memory/`, 5 archivos JSON que persisten entre sesiones.

**¿Cómo funciona la protección de construcciones?**
De dos maneras: ① Registro manual ② Detección automática (escaneo cada 60 segundos).

**¿Qué proveedores de IA son compatibles?**
Formato compatible con OpenAI (incluyendo DeepSeek/OpenRouter/MiMo, etc.) + formato Anthropic.

**¿Cuánto pesa la imagen de Docker?**
Aproximadamente 200MB, basada en python:3.11-slim con compilación multi-etapa.

---

## 🗺️ Hoja de ruta

### v3.0 (actual) ✅
- [x] Sistema de memoria de tres capas (espacial/ruta/estrategia)
- [x] Navegación inteligente (impulsada por memoria + integración con Baritone)
- [x] Arquitectura de doble Agente (aislamiento chat/operaciones)
- [x] Protección automática de zonas de construcción
- [x] Miuix Console WebUI
- [x] Despliegue con un clic en Windows/Linux
- [x] Imagen Docker + publicación automática en GHCR
- [x] GitHub Actions CI/CD

### v3.1 (planificado)
- [ ] Entrada multimodal (análisis de capturas de pantalla)
- [ ] Mercado de Skills (importación/exportación)
- [ ] Colaboración multijugador
- [ ] Interacción por voz

---

## 📄 Licencia

MIT License. Consulta [LICENSE](LICENSE) para más detalles.
