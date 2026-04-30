# 🧠 BlockMind — Sistema de Companheiro Inteligente para Minecraft

> **Fabric Mod + IA + Sistema de Memória** · v3.0 · 2026-04-30

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![Fabric](https://img.shields.io/badge/Fabric-0.92+-yellow.svg)](https://fabricmc.net)
[![MC](https://img.shields.io/badge/Minecraft-1.20.x--1.21.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**Resumo em uma frase:** Fabric Mod fornece interfaces precisas do jogo + backend Python conduz decisões de IA + sistema de memória aprende entre sessões, resultando em um companheiro inteligente Minecraft autônomo 24/7.

🌐 [中文](README.md) | [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | [Español](README-es.md) | [Français](README-fr.md) | [Bahasa Indonesia](README-id.md) | [Italiano](README-it.md) | **Português** | [Русский](README-ru.md) | [ภาษาไทย](README-th.md) | [Türkçe](README-tr.md) | [Tiếng Việt](README-vi.md)
---

## 📖 Índice

- [Diferenciais do Projeto](#-diferenciais-do-projeto)
- [Arquitetura do Sistema](#-arquitetura-do-sistema)
- [Sistema de Memória](#-sistema-de-memória)
- [Navegação Inteligente](#-navegação-inteligente)
- [Arquitetura de Duplo Agente](#-arquitetura-de-duplo-agente)
- [Início Rápido](#-início-rápido)
- [Implantação com Um Clique](#-implantação-com-um-clique)
- [API do Fabric Mod](#-api-do-fabric-mod)
- [Sistema Skill DSL](#-sistema-skill-dsl)
- [Sistema de Segurança](#-sistema-de-segurança)
- [Painel de Controle WebUI](#-painel-de-controle-webui)
- [Guia de Implantação](#-guia-de-implantação)
- [FAQ](#-faq)
- [Roteiro](#-roteiro)

---

## ✨ Diferenciais do Projeto

### 🧠 Sistema de Memória — Aprendizado entre Sessões (Novo no v3.0)

```
Modo tradicional:  Esquece tudo a cada reinício, repete erros, gasta Tokens desnecessariamente
Com memória:       Três camadas (espaço/rotas/estratégias), JSON persistente, reutilização entre sessões
```

- **Memória Espacial**: Detecta e lembra automaticamente zonas de proteção de construções, áreas perigosas e pontos de recursos
- **Memória de Rotas**: Cacheia rotas bem-sucedidas, bloqueia rotas falhas, estatísticas de taxa de sucesso
- **Memória de Estratégias**: Operações bem-sucedidas se tornam automaticamente estratégias reutilizáveis, zero consumo de Token
- **Proteção de Construções**: Navega automaticamente evitando construções de jogadores, sem risco de destruir casas

### 🛤️ Navegação Inteligente — Busca de Caminho Orientada por Memória (Novo no v3.0)

```
Modo tradicional:  walk_to(x,y,z) → Travou na parede / Destruiu construção
Navegação inteligente: Consulta memória → Usa cache → Baritone( exclui zonas protegidas) → Fallback A*
```

- **Prioridade ao Cache**: Caminhos percorridos são reutilizados diretamente, sem cálculo
- **Integração com Baritone**: Motor de busca de caminho mais poderoso da comunidade, cava caminhos/constrói pontes/nada/desvia lava automaticamente
- **Injeção de Zonas de Proteção**: Construções na memória são injetadas automaticamente como zonas de exclusão do Baritone
- **Aprendizado Automático**: Cada resultado de navegação é registrado automaticamente no sistema de memória

### 🤖 Arquitetura de Duplo Agente — Isolamento entre Chat e Operações (Novo no v2.0)

```
Agente Principal:   Responsável pelo chat, contexto persistente, apenas identificação de intenção (~50 Tokens/chamada)
Agente de Operação: Responsável pela execução, sem estado, contexto novo a cada chamada (<1500 Tokens/chamada)
```

- **Agente Principal**: Mantém contexto da conversa, identifica tags `[TASK:xxx]`
- **Agente de Operação**: Sem estado, descartado após uso, evita explosão de contexto
- **Injeção de Memória**: Contexto de memória injetado automaticamente durante decisões da IA (zonas de proteção, rotas conhecidas, etc.)

### 🔌 Arquitetura do Fabric Mod — Precisa e Confiável

- **Zero Parsing de Protocolo**: Chamada direta à API interna do jogo
- **13 Endpoints HTTP** + Eventos em tempo real via WebSocket
- **Integração Baritone Opcional**: Com Baritone busca avançada, sem ele busca linear básica

### 🛡️ Sistema de Segurança em Cinco Níveis

| Nível | Nome | Exemplo | Estratégia |
|-------|------|---------|------------|
| 0 | Completamente Seguro | Mover, Pular | Execução automática |
| 1 | Baixo Risco | Escavar terra, colocar tocha | Execução automática |
| 2 | Médio Risco | Minerar minério, atacar criaturas neutras | Execução automática |
| 3 | Alto Risco | Acender TNT, colocar lava | Requer autorização do jogador |
| 4 | Risco Fatal | Colocar bloco de comando | Proibido por padrão |

---

## 🏗️ Arquitetura do Sistema

```
┌──────────────────────────────────────────────────────────────┐
│                  Servidor Minecraft                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │           BlockMind Fabric Mod (Java)                  │  │
│  │                                                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Coletor   │ │Executor  │ │Listener  │ │Baritone  │ │  │
│  │  │de Estado │ │de Ações  │ │de Eventos│ │Motor de  │ │  │
│  │  │Bloco/   │ │Mover/   │ │Chat/Dano/│ │caminhos  │ │  │
│  │  │Entidade/ │ │Cavar/   │ │Mudança de│ │(opcional)│ │  │
│  │  │Inventário│ │Colocar/  │ │bloco     │ │          │ │  │
│  │  │/Mundo    │ │Atacar    │ │          │ │          │ │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │  │
│  │       └─────────────┼────────────┼────────────┘       │  │
│  │               HTTP API :25580 + WebSocket              │  │
│  └─────────────────────────────┼──────────────────────────┘  │
└────────────────────────────────┼─────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────┐
│              Backend Python BlockMind                         │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            Arquitetura de Duplo Agente                 │  │
│  │  ┌─────────────────┐  ┌────────────────────────────┐  │  │
│  │  │Agente Principal │  │Agente de Operação          │  │  │
│  │  │(Chat)           │  │(Execução, sem estado)      │  │  │
│  │  │Contexto         │  │Contexto novo a cada        │  │  │
│  │  │persistente      │  │chamada                     │  │  │
│  │  │Identificação de │  │Match/Geração/Execução      │  │  │
│  │  │intenção         │  │de Skills                   │  │  │
│  │  └────────┬────────┘  └─────────────┬──────────────┘  │  │
│  └───────────┼─────────────────────────┼─────────────────┘  │
│              │                         │                     │
│  ┌───────────▼─────────────────────────▼─────────────────┐  │
│  │              🧠 Sistema de Memória (GameMemory)        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Memória   │ │Memória de│ │Memória de│ │Memória   │ │  │
│  │  │Espacial  │ │Rotas     │ │Estratégias│ │do Jogador│ │  │
│  │  │Zonas de  │ │Rotas     │ │Estratégias│ │Local da  │ │  │
│  │  │proteção  │ │bem-suced.│ │de sucesso│ │casa      │ │  │
│  │  │Áreas     │ │Lista negra│ │Registros │ │Preferên- │ │  │
│  │  │perigosas │ │de falhas │ │de falhas │ │cias      │ │  │
│  │  │Pontos de │ │Estatísti-│ │Tags de   │ │Registros │ │  │
│  │  │recursos  │ │cas       │ │contexto  │ │de intera-│ │  │
│  │  │          │ │          │ │          │ │ção       │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │  │
│  │              JSON persistente (data/memory/)            │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │ Injeção                       │
│  ┌──────────┐ ┌──────────────▼──────┐ ┌──────────────────┐  │
│  │Motor     │ │Navegação           │ │Camada de Decisão │  │
│  │Skill     │ │Inteligente         │ │da IA             │  │
│  │Parsing   │ │Memória→Cache→      │ │Injeção de        │  │
│  │Match/    │ │Baritone→Fallback   │ │contexto de       │  │
│  │Execução  │ │A*→Auto-aprendizado │ │memória           │  │
│  └──────────┘ └─────────────────────┘ │provider.py       │  │
│  ┌──────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │Validação │ │Monitoramento│ │ WebUI (Miuix Console)    │ │
│  │de Segur. │ │de Saúde     │ │ Tema escuro/Config.      │ │
│  │Risco 5lv │ │3 níveis de  │ │ de modelos               │ │
│  └──────────┘ │degradação   │ └──────────────────────────┘ │
│               └──────────────┘                               │
└──────────────────────────────────────────────────────────────┘
```

### Exemplo de Fluxo de Dados

**Navegação inteligente orientada por memória:**
```
Jogador diz "ir para casa"
  → Agente Principal identifica tarefa [TASK:ir para casa]
  → Agente de Operação faz match com Skill go_home
  → SmartNavigator consulta memória:
      ✅ Local da casa: (65, 64, -120) da memória do jogador
      ✅ Rota em cache: Percorrida 3 vezes, taxa de sucesso 100%
      ✅ Zona de proteção: Raio de 30 blocos ao redor da base, proibido destruir
      ✅ Área perigosa: (80,12,-50) tem lava
  → Navegação com Baritone:
      GoalBlock(65, 64, -120)
      + exclusion_zones=[zona de proteção da base]
      → Desvia automaticamente, sem destruir nenhuma construção
  → Ao chegar: cache da rota success_count+1
  → Próxima vez que for para casa: usa rota em cache diretamente, zero consumo de Token
```

---

## 🧠 Sistema de Memória

### Arquitetura de Três Camadas de Memória

| Camada | Conteúdo Armazenado | Persistência | Exemplo |
|--------|---------------------|--------------|---------|
| **Memória Espacial** | Zonas de proteção, áreas perigosas, pontos de recursos, base | ✅ JSON | "Área da base: (50-100, 60-80, -150--90)" |
| **Memória de Rotas** | Cache de rotas bem-sucedidas, lista negra de rotas falhas, taxa de sucesso | ✅ JSON | "Casa→Mina: passando por (70,64,-100) taxa de sucesso 100%" |
| **Memória de Estratégias** | Estratégias de sucesso consolidadas, lições de falhas, tags de contexto | ✅ JSON | "Ao minerar, coloque tochas primeiro — maior eficiência" |
| **Memória do Jogador** | Local da casa, ferramentas preferidas, registros de interação | ✅ JSON | "A casa do Steve fica em (100,64,200)" |
| **Memória do Mundo** | Ponto de spawn, pontos seguros, eventos importantes | ✅ JSON | "Spawn (0,64,0), lista de pontos seguros" |

### Proteção Automática de Construções

```python
# Registrar zona de proteção de construção (IA proibida de destruir)
memory.register_building("Cidade Principal", center=(100, 64, 200), radius=30)
# → Injetado automaticamente como exclusion_zones do Baritone durante navegação
# → type: "no_break" + "no_place"
# → IA não consegue destruir/colocar blocos dentro da zona protegida

# Detecção automática (escaneia arredores a cada 60 segundos)
navigator.auto_detect_and_memorize()
# → Detecta blocos de construção contínuos → registra automaticamente como zona protegida
# → Detecta lava/fogo → registra automaticamente como área perigosa
# → Detecta acúmulo de minérios → registra automaticamente como ponto de recursos
```

### Mecanismo de Cache de Rotas

```python
# Primeira navegação: IA planeja + executa
result = await navigator.goto(100, 64, 200)
# → Cacheia rota: success_count=1, success_rate=100%

# Segunda navegação: usa cache diretamente
result = await navigator.goto(100, 64, 200)
# → Cache hit, execução direta, zero cálculo

# Rota falha: aprendizado automático
# → fail_count >= 3 → adicionada à lista negra automaticamente
# → Próxima vez replaneja, não repete o mesmo caminho
```

### Consolidação Automática de Estratégias

```python
# Registrado automaticamente após sucesso do Agente de Operação
memory.record_strategy(
    task_type="mine",
    description="Colocar tochas antes de minerar",
    action_sequence=[...],
    success=True,
    context_tags=["nighttime", "cave"],
)

# Próxima tarefa do mesmo tipo faz match com a melhor estratégia automaticamente
best = memory.get_best_strategy("mine", context_tags=["nighttime"])
# → Retorna a estratégia com maior taxa de sucesso
```

### Injeção de Contexto de Memória na IA

```python
# Contexto de memória injetado automaticamente a cada decisão da IA
memory_context = memory.get_ai_context()
# Saída:
# [Sistema de Memória]
# Base:
#   - Casa: (50, 64, -100) (raio 30)
# Zonas de proteção (proibido destruir):
#   - Cidade Principal: (100, 64, 200) (raio 20)
# Áreas perigosas:
#   - Lago de lava: (80, 12, -50) (lava)
# Rotas confiáveis conhecidas: 3
# Estratégias verificadas: 5
```

---

## 🛤️ Navegação Inteligente

### Fluxo de Navegação

```
SmartNavigator.goto(x, y, z)
  │
  ├── 1. Verificação de segurança
  │     └── Destino dentro de zona protegida? → Alerta mas não recusa
  │
  ├── 2. Consulta cache de rotas
  │     └── Cache confiável disponível? → Executa rota do cache diretamente
  │
  ├── 3. Obter contexto de navegação
  │     ├── Zonas de exclusão (zonas de proteção)
  │     ├── Áreas perigosas (lava, penhascos)
  │     └── Referência de rotas confiáveis
  │
  ├── 4. Busca de caminho com Baritone (prioridade)
  │     ├── Injeta exclusion_zones
  │     ├── Cava caminhos / Constrói pontes / Nada automaticamente
  │     └── Custo de queda / Evita lava
  │
  ├── 5. Busca de caminho com A* (fallback)
  │     └── A* em grade básica + verificação de transponibilidade
  │
  └── 6. Registrar resultado
        ├── Sucesso → cache_path(success=True)
        └── Falha → cache_path(success=False) + possível lista negra
```

### Integração com Baritone

| Recurso | Baritone | A* Básico |
|---------|----------|-----------|
| Algoritmo de busca | A* melhorado + heurística de custo | A* padrão |
| Cavar caminhos | ✅ Cava automaticamente através de obstáculos | ❌ |
| Construir pontes | ✅ Modo scaffold | ❌ |
| Nadar | ✅ | ❌ |
| Movimento vertical | ✅ Pulo/escada/trepadeira | ⚠️ Apenas 1 bloco |
| Evitar lava | ✅ Penalidade de custo | ❌ |
| Custo de queda | ✅ Incluído na heurística | ❌ |
| Zonas de exclusão | ✅ `exclusionAreas` | ❌ |
| **Proteção de construções** | ✅ Injeta zonas `no_break` | ❌ |

### Tipos de Zonas de Exclusão

| Tipo | Descrição | Origem |
|------|-----------|--------|
| `no_break` | Proíbe destruição de blocos | Zona de proteção, base |
| `no_place` | Proíbe colocação de blocos | Zona de proteção |
| `avoid` | Desvia completamente | Área perigosa (lava, etc.) |

---

## 🤖 Arquitetura de Duplo Agente

### Por que Precisamos de Dois Agentes?

```
Problema com agente único:
  Contexto de chat + contexto de operação → Explosão de Tokens (>4000/chamada)
  Falha na operação contamina o chat → Experiência ruim
  Cada operação carrega histórico completo do chat → Desperdício

Solução com duplo agente:
  Agente Principal: Apenas chat, janela deslizante de 20 mensagens, ~50 Tokens/chamada
  Agente de Operação: Sem estado, contexto novo a cada chamada, <1500 Tokens/chamada
```

### Fluxo

```
Mensagem do jogador
  → Agente Principal faz o chat (contexto persistente)
  → Identifica tag [TASK:xxx]
  → Extrai descrição da tarefa
  → Agente de Operação executa (sem estado):
      ├── Busca/match de Skill
      ├── Injeta contexto de memória
      ├── L1/L2: Executa Skill em cache
      ├── L3: IA preenche template + executa
      └── L4: IA faz raciocínio completo + executa
  → Agente Principal formata resposta → Jogador
```

---
## 🚀 Início Rápido

### Requisitos do Ambiente

| Componente | Requisito |
|------------|-----------|
| Python | 3.10+ |
| Java | 17+ |
| Minecraft | 1.19.4 - 1.21.4 |
| Fabric Loader | 0.15+ |

---

## 📦 Implantação com Um Clique

### Download

Baixe a partir do [GitHub Releases](https://github.com/bmbxwbh/BlockMind/releases/latest):

| Arquivo | Descrição |
|---------|-----------|
| `blockmind-mod-1.0.0.jar` | Fabric Mod (coloque na pasta mods/ do servidor) |
| `Source code` (zip/tar) | Código-fonte completo |

### Início com Um Clique no Linux / macOS

```bash
# Clonar
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

# Início com um clique (instala dependências + servidor MC + BlockMind + WebUI automaticamente)
chmod +x start.sh
./start.sh
```

> `start.sh` faz automaticamente: Detecta Python/Java → Instala dependências → Escaneia servidor MC existente → Seleciona versão e instala → Inicia tudo

### Início com Um Clique no Windows

```cmd
:: Clonar (ou baixe o zip e extraia)
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

:: Instalação com um clique
install.bat

:: Início com um clique (servidor MC + BlockMind + WebUI)
start_all.bat
```

> Veja o passo a passo detalhado no [Guia de Implantação Windows](docs/WINDOWS.md)

### Implantação com Docker

```bash
# Baixar imagem
docker pull ghcr.io/bmbxwbh/blockmind:latest

# Baixar template de configuração
wget https://raw.githubusercontent.com/bmbxwbh/BlockMind/main/config.example.yaml -O config.yaml
# Edite o config.yaml com a configuração do seu modelo de IA

# Iniciar
docker run -d \
  --name blockmind \
  -p 19951:19951 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v blockmind-data:/data \
  ghcr.io/bmbxwbh/blockmind:latest
```

Ou use docker-compose:

```bash
git clone https://github.com/bmbxwbh/BlockMind.git && cd BlockMind
cp config.example.yaml config.yaml
# Edite o config.yaml
docker compose up -d
```

```bash
# Ver logs
docker compose logs -f blockmind
# Parar
docker compose down
```

### Configuração

Edite o `config.yaml`:

```yaml
ai:
  main_agent:
    provider: "openai"          # openai ou anthropic
    api_key: "sk-your-key"
    model: "gpt-4o"             # Nome do seu modelo
    base_url: ""                # URL personalizada da API (opcional)

webui:
  enabled: true
  port: 19951
  auth:
    password: "your-password"   # Senha de login do WebUI
```

Após iniciar, acesse `http://localhost:19951` para abrir o painel de controle.

---

## 🔌 API do Fabric Mod

### Consulta de Estado

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/health` | GET | Verificação de saúde |
| `/api/status` | GET | Estado do jogador |
| `/api/world` | GET | Estado do mundo |
| `/api/inventory` | GET | Informações do inventário |
| `/api/entities?radius=32` | GET | Entidades próximas |
| `/api/blocks?radius=16` | GET | Blocos próximos |

### Execução de Ações

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/move` | POST | Mover para coordenada |
| `/api/dig` | POST | Escavar bloco |
| `/api/place` | POST | Colocar bloco |
| `/api/attack` | POST | Atacar entidade |
| `/api/eat` | POST | Comer |
| `/api/look` | POST | Olhar para coordenada |
| `/api/chat` | POST | Enviar mensagem no chat |

### Planejamento de Rota

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/pathfind` | POST | Navegação por caminho (Baritone/A*) |
| `/api/pathfind/stop` | POST | Parar navegação |
| `/api/pathfind/status` | GET | Estado da navegação |

### Eventos Push

O Mod envia eventos via WebSocket:
- `player_damaged` — Jogador ferido
- `entity_attack` — Atacado
- `health_low` — Vida baixa
- `inventory_full` — Inventário cheio
- `block_broken` — Escavação de bloco concluída

---

## 📝 Sistema Skill DSL

### Classificação de Tarefas

| Nível | Tipo | Exemplo | Estratégia de Cache |
|-------|------|---------|---------------------|
| L1 | Tarefa fixa | "Ir para casa" | Execução direta |
| L2 | Tarefa parametrizada | "Minerar 10 diamantes" | Cache com parâmetros |
| L3 | Tarefa com template | "Construir um abrigo" | Match de template |
| L4 | Tarefa dinâmica | "Me ajude a derrotar o Ender Dragon" | Raciocínio da IA |

### Exemplo de Skill em YAML

```yaml
skill_id: mine_diamonds
name: "Minerar diamantes"
level: L2
parameters:
  count: {type: int, default: 10, min: 1, max: 64}
steps:
  - action: pathfind
    target: {y: -59}
    note: "Ir para a camada de diamantes"
  - action: dig_loop
    block: diamond_ore
    count: ${count}
  - action: pathfind
    target: home
    note: "Voltar para a base"
```

---

## 🛡️ Sistema de Segurança

| Camada | Mecanismo | Descrição |
|--------|-----------|-----------|
| L1 | Avaliação de risco | Cada ação pontuada de 0-100 |
| L2 | Autorização de operação | Alto risco requer confirmação |
| L3 | Intervenção de emergência | Jogador pode interromper a IA a qualquer momento |
| L4 | Log de auditoria | Todas as operações são rastreáveis |
| L5 | Restrição de zona segura | Limita alcance de destruição/colocação |

---

## 🖥️ Painel de Controle WebUI

Após iniciar, acesse `http://localhost:19951`, com suporte a:

- 📊 Dashboard — Monitoramento de estado em tempo real
- 🛠️ Gerenciamento de Skills — Edição online de YAML
- 🧠 Sistema de Memória — Visualizar/Limpar/Backup
- 🤖 Configuração de Modelos — Troca de modelos de IA em tempo real
- 💬 Painel de Comandos — Instruções em linguagem natural
- 📋 Fila de Tarefas — Visualizar estado de execução
- 📝 Central de Logs — Fluxo de logs em tempo real

---

## ❓ FAQ

**P: É obrigatório instalar o Baritone?**
R: Não. O Baritone é uma dependência opcional. Sem ele, o sistema faz fallback automaticamente para o A* básico em linha reta.

**P: Onde os dados de memória são armazenados?**
R: No diretório `data/memory/`, em 5 arquivos JSON, preservados entre sessões.

**P: Como a proteção de construções funciona?**
R: De duas formas: ① Registro manual ② Detecção automática (escaneamento a cada 60 segundos).

**P: Quais provedores de IA são suportados?**
R: Formato compatível com OpenAI (incluindo DeepSeek/OpenRouter/MiMo etc.) + formato Anthropic.

**P: Qual o tamanho da imagem Docker?**
R: Aproximadamente 200MB, construída com multi-stage build baseado em python:3.11-slim.

---

## 🗺️ Roteiro

### v3.0 (Atual) ✅
- [x] Sistema de memória em três camadas (espaço/rotas/estratégias)
- [x] Navegação inteligente (orientada por memória + integração Baritone)
- [x] Arquitetura de duplo agente (isolamento chat/operação)
- [x] Proteção automática de zonas de construção
- [x] WebUI Miuix Console
- [x] Implantação com um clique Windows/Linux
- [x] Imagem Docker + publicação automática no GHCR
- [x] CI/CD com GitHub Actions

### v3.1 (Planejado)
- [ ] Entrada multimodal (análise de capturas de tela)
- [ ] Marketplace de Skills (importar/exportar)
- [ ] Colaboração multijogador
- [ ] Interação por voz

---

## 📄 Licença

MIT License. Veja os detalhes em [LICENSE](LICENSE).
