# 🧠 BlockMind

> **Fabric Mod + AI + 기억 시스템** · Minecraft AI 동반자

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![MC](https://img.shields.io/badge/Minecraft-1.20~26.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT--NC-purple.svg)](LICENSE)

Fabric Mod가 정밀한 게임 인터페이스를 제공하고, Python 백엔드가 AI 의사결정을 구동하며, 기억 시스템이 세션 간 학습을 실현. **서버와 클라이언트 모드를 모두 지원** — 싱글플레이, LAN, 서버에서 사용 가능.

🌐 [中文](README.md) | [English](README-en.md) | [日本語](README-ja.md) | **한국어** | [العربية](README-ar.md) | [Deutsch](README-de.md) | [Español](README-es.md) | [Français](README-fr.md)

---

## BlockMind를 선택하는 이유

### 1. 기억 시스템 — 학습하는 AI

기존 AI 동반자는 재시작할 때마다 모든 것을 잊는다. BlockMind는 3계층 영속 기억을 갖는다:

- **공간 기억**: 건축 보호 구역, 위험 지역, 자원 포인트를 자동 기억
- **경로 기억**: 성공 경로를 캐싱하고, 실패 경로를 블랙리스트에 등록, 다음에 바로 재사용
- **전략 기억**: 성공적인 작업이 자동으로 재사용 가능한 전략으로 축적, Token 소비 Zero

내비게이션 시 플레이어 건물을 자동 우회, 기지를 파괴하지 않는다.

### 2. 이중 Agent 아키텍처 — Token 절약

```
메인 Agent (~50 Token/회): 채팅 + 의도 인식만
작업 Agent (<1500 Token/회): 무상태, 일회용 실행
```

단일 Agent 방안(>4000 Token/회) 대비 84% 비용 절감.

### 3. 서버 + 클라이언트 듀얼 모드

| 모드 | 설치 위치 | 플레이어 | 시나리오 |
|------|----------|---------|---------|
| 서버 | 서버 `mods/` | FakePlayer (Bot) | 서버 7×24 방치 |
| 클라이언트 | 클라이언트 `mods/` | 로컬 플레이어 | 싱글플레이 / LAN |

### 4. Baritone 통합 + 건축 보호

AI는 Baritone으로 경로 탐색(자동 굴기/다리 놓기/수영)을 하지만, 건축 보호 구역을 자동 우회한다. 기억된 건축물이 실시간으로 Baritone 제외 영역에 주입된다.

### 5. Skill DSL + 마켓플레이스

YAML로 재사용 가능한 AI 스킬(채굴, 농사, 건축)을 정의하고, 커뮤니티와 공유. AI가 생성한 스킬은 자동 저장, 다음 실행 시 Token 소비 Zero.

---

## 빠른 시작

### 환경 요구사항

- Python 3.10+ · Java 17+ · Minecraft 1.20.0 ~ 26.1.2

### 원클릭 시작

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

### 설정

`config.yaml` 편집:

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

시작 후 `http://localhost:19951`에서 제어 패널 접속.

---

## 아키텍처

```
┌──────────────── Minecraft ────────────────┐
│  BlockMind Fabric Mod (Java)              │
│  상태 수집 · 동작 실행                    │
│  이벤트 리스닝                             │
│  HTTP API :25580 · WebSocket              │
└──────────────────┬────────────────────────┘
                   │
┌──────────────────▼────────────────────────┐
│  BlockMind Python 백엔드                   │
│  ┌──────────┐  ┌──────────────────────┐  │
│  │ 메인     │  │ 작업 Agent           │  │
│  │ Agent    │  │ (무상태)             │  │
│  │ 채팅+    │  │ Skill 매칭/생성/     │  │
│  │ 의도파악 │  │ 실행                 │  │
│  └─────┬────┘  └──────────┬───────────┘  │
│  ┌─────▼──────────────────▼───────────┐  │
│  │ 기억 시스템 · 지능형 내비게이션     │  │
│  │ · Skill 엔진                      │  │
│  └────────────────┬───────────────────┘  │
│  ┌────────────────▼───────────────────┐  │
│  │ WebUI 제어 패널 (MiuiX)            │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## WebUI 제어 패널

`http://localhost:19951` — Lucide 아이콘 + MiuiX 다크 테마

| 기능 | 설명 |
|------|------|
| 대시보드 | 실시간 상태, 빠른 명령, 이벤트 스트림 |
| Skill 관리 | 온라인 YAML 편집, 원클릭 실행 |
| Skill 마켓 | 커뮤니티 스킬 탐색, 설치, 가져오기/내보내기 |
| 기억 시스템 | 조회 / 백업 / 정리 / 가져오기/내보내기 |
| 모델 설정 | 이중 Agent 모델 설정, 핫스위칭 |
| 보안 설정 | 위험 등급, 감사 로그 |
| 작업 대기열 | 실행 상태 모니터링 |
| 로그 센터 | 실시간 WebSocket 로그 스트림 |

---

## Fabric Mod API

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/status` | GET | 플레이어 상태 |
| `/api/inventory` | GET | 인벤토리 정보 |
| `/api/entities` | GET | 주변 엔티티 |
| `/api/move` | POST | 좌표로 이동 |
| `/api/dig` | POST | 블록 채굴 |
| `/api/place` | POST | 블록 배치 |
| `/api/attack` | POST | 엔티티 공격 |
| `/api/chat` | POST | 채팅 전송 |

전체 API 문서: [Fabric Mod API](docs/MOD_BUILD.md).

---

## 지원 버전

| MC 버전 | Java | 상태 |
|---------|------|------|
| 1.20.0 ~ 1.20.6 | 17~21 | ✅ |
| 1.21 ~ 1.21.4 | 21 | ✅ |
| 26.1 ~ 26.1.2 | 25 | ✅ 최신 |

---

## FAQ

**Q: Baritone을 반드시 설치해야 하나요?** 아닙니다. 없으면 기본 A*로 폴백됩니다.

**Q: 기억 데이터는 어디에 저장되나요?** `data/memory/` 디렉토리의 5개 JSON 파일입니다.

**Q: 어떤 AI 모델을 지원하나요?** OpenAI 호환 형식(DeepSeek/OpenRouter/MiMo) + Anthropic.

**Q: 싱글플레이에서 사용할 수 있나요?** 네, 클라이언트 `mods/` 폴더에 Mod를 넣으면 됩니다.

---

## 라이선스

MIT-NC — 상업적 사용 금지. 자세한 내용은 [LICENSE](LICENSE) 참조.
