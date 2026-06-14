# 🧠 BlockMind

> **Mod Fabric + IA + Sistema de Memória** · Companheiro inteligente Minecraft

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![MC](https://img.shields.io/badge/Minecraft-1.20~26.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT--NC-purple.svg)](LICENSE)

O Mod Fabric fornece interfaces precisas do jogo + o backend Python conduz decisões de IA + o sistema de memória aprende entre sessões. **Suporta servidor e client**, utilizável em individual, LAN ou servidores.

🌐 [中文](README.md) | [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | [Español](README-es.md) | [Français](README-fr.md)

---

## Por que BlockMind

### 1. Sistema de memória — A IA aprende

Os companheiros de IA tradicionais esquecem tudo ao reiniciar. BlockMind tem três camadas de memória persistente:

- **Memória espacial**: Lembra automaticamente zonas de construção protegidas, áreas perigosas e pontos de recursos
- **Memória de rotas**: Armazena rotas bem-sucedidas, bloqueia as falhas, reutiliza na próxima vez
- **Memória de estratégias**: Operações bem-sucedidas se consolidam como estratégias reutilizáveis, consumo zero de tokens

A IA navega evitando automaticamente as construções do jogador, nunca destrói a casa.

### 2. Arquitetura de duplo Agente — Economia de tokens

```
Agente principal (~50 tokens/chamada): Apenas chat + identificação de intenção
Agente de operações (<1500 tokens/chamada): Execução sem estado, descartável
```

Comparado a um agente único (>4000 tokens/chamada), economia de 84% nos custos.

### 3. Servidor + Client dual

| Modo | Localização | Jogador | Cenário |
|------|-------------|---------|---------|
| Servidor | `mods/` do servidor | FakePlayer (Bot) | Servidor 7×24 |
| Client | `mods/` do client | Jogador local | Individual / LAN |

### 4. Baritone integrado + proteção de construções

A IA usa Baritone para pathfinding (escavação/pontes/natação automáticos), mas evita automaticamente as zonas de construção protegidas. As construções em memória são injetadas como zonas de exclusão do Baritone em tempo real.

### 5. Skill DSL + marketplace

Defina habilidades de IA reutilizáveis em YAML (mineração, agricultura, construção), compartilhadas com a comunidade. As habilidades geradas pela IA são salvas automaticamente, execução sem tokens na próxima vez.

---

## Início rápido

### Requisitos

- Python 3.10+ · Java 17+ · Minecraft 1.20.0 ~ 26.1.2

### Um clique Linux/macOS

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

### Configuração

Edite `config.yaml`:

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

Acesse `http://localhost:19951` para o painel de controle.

---

## Arquitetura

```
┌──────────────── Minecraft ────────────────┐
│  BlockMind Fabric Mod (Java)              │
│  Coleta · Execução · Eventos              │
│  HTTP API :25580 · WebSocket              │
└──────────────────┬────────────────────────┘
                   │
┌──────────────────▼────────────────────────┐
│  Backend Python BlockMind                 │
│  ┌──────────┐  ┌──────────────────────┐  │
│  │Agente    │  │Agente de operações   │  │
│  │principal │  │(sem estado)          │  │
│  │Chat+iden.│  │Match/exec. Skills    │  │
│  └─────┬────┘  └──────────┬───────────┘  │
│  ┌─────▼──────────────────▼───────────┐  │
│  │Memória · Navegação · Skills        │  │
│  └────────────────┬───────────────────┘  │
│  ┌────────────────▼───────────────────┐  │
│  │WebUI (MiuiX)                      │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## Painel de controle WebUI

`http://localhost:19951` — Ícones Lucide + tema escuro MiuiX

| Função | Descrição |
|--------|-----------|
| Dashboard | Estado em tempo real, atalhos, fluxo de eventos |
| Skills | Edição YAML online, execução com um clique |
| Marketplace | Explorar/instalar/importar/exportar skills da comunidade |
| Memória | Visualizar/backup/limpar/importar/exportar |
| Modelos | Configuração dual de agentes, troca em tempo real |
| Segurança | Níveis de risco, log de auditoria |
| Fila de tarefas | Monitoramento do estado de execução |
| Logs | Fluxo de logs em tempo real via WebSocket |

---

## API do Fabric Mod

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/status` | GET | Estado do jogador |
| `/api/inventory` | GET | Informações do inventário |
| `/api/entities` | GET | Entidades próximas |
| `/api/move` | POST | Mover para coordenadas |
| `/api/dig` | POST | Escavar bloco |
| `/api/place` | POST | Colocar bloco |
| `/api/attack` | POST | Atacar entidade |
| `/api/chat` | POST | Enviar mensagem no chat |

Documentação completa em [API Fabric Mod](docs/MOD_BUILD.md).

---

## Versões suportadas

| MC | Java | Estado |
|----|------|--------|
| 1.20.0 ~ 1.20.6 | 17~21 | ✅ |
| 1.21 ~ 1.21.4 | 21 | ✅ |
| 26.1 ~ 26.1.2 | 25 | ✅ Última |

---

## FAQ

**É obrigatório instalar Baritone?** Não, sem ele o sistema usa A* básico.

**Onde os dados de memória são salvos?** Em `data/memory/`, 5 arquivos JSON.

**Quais modelos de IA são suportados?** Formato OpenAI (DeepSeek/OpenRouter/MiMo) + Anthropic.

**Funciona em modo individual?** Sim, coloque o Mod em `mods/` do client.

---

## Licença

MIT-NC — Uso não comercial. Ver [LICENSE](LICENSE).
