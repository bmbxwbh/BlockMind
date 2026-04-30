# 🧠 BlockMind — 지능형 Minecraft AI 동반자 시스템

> **Fabric Mod + AI 기반 + 기억 시스템** · v3.0 · 2026-04-30

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![Fabric](https://img.shields.io/badge/Fabric-0.92+-yellow.svg)](https://fabricmc.net)
[![MC](https://img.shields.io/badge/Minecraft-1.20.x--1.21.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**한 줄 요약:** Fabric Mod가 정밀한 게임 인터페이스를 제공하고, Python 백엔드가 AI 의사결정을 구동하며, 기억 시스템이 세션 간 학습을 통해 7×24 자율 생존이 가능한 Minecraft 지능형 동반자를 구현합니다.

🌐 [中文](README.md) | [English](README-en.md) | [日本語](README-ja.md) | **한국어** | [العربية](README-ar.md) | [Deutsch](README-de.md) | [Español](README-es.md) | [Français](README-fr.md) | [Bahasa Indonesia](README-id.md) | [Italiano](README-it.md) | [Português](README-pt.md) | [Русский](README-ru.md) | [ภาษาไทย](README-th.md) | [Türkçe](README-tr.md) | [Tiếng Việt](README-vi.md)
---

## 📖 목차

- [프로젝트 특징](#-프로젝트-특징)
- [시스템 아키텍처](#-시스템-아키텍처)
- [기억 시스템](#-기억-시스템)
- [지능형 내비게이션](#-지능형-내비게이션)
- [이중 Agent 아키텍처](#-이중-agent-아키텍처)
- [빠른 시작](#-빠른-시작)
- [원클릭 배포](#-원클릭-배포)
- [Fabric Mod API](#-fabric-mod-api)
- [Skill DSL 시스템](#-skill-dsl-시스템)
- [보안 체계](#-보안-체계)
- [WebUI 제어 패널](#-webui-제어-패널)
- [배포 가이드](#-배포-가이드)
- [FAQ](#-faq)
- [로드맵](#-로드맵)

---

## ✨ 프로젝트 특징

### 🧠 기억 시스템 — 세션 간 학습 (v3.0 신규)

```
기존 방식:  매 재시작마다 모든 것을 잊고, 같은 실수를 반복하며, Token을 반복 소비
기억 방식:  공간/경로/전략 3계층 기억, JSON 영속화, 세션 간 재사용
```

- **공간 기억**: 건축 보호 구역, 위험 지역, 자원 포인트를 자동 감지 및 기억
- **경로 기억**: 성공 경로를 캐싱하고, 실패 경로를 블랙리스트에 등록하며, 성공률을 통계 관리
- **전략 기억**: 성공적인 작업이 자동으로 재사용 가능한 전략으로 추출되며, Zero Token으로 재사용
- **건축 보호**: 내비게이션 시 플레이어 건물을 자동으로 우회하여 건물 파괴 방지

### 🛤️ 지능형 내비게이션 — 기억 기반 경로 탐색 (v3.0 신규)

```
기존 방식:  walk_to(x,y,z) → 벽에 막힘 / 건물 파괴
지능형 내비게이션:  기억 조회 → 캐시 이동 → Baritone(보호 구역 제외) → A* 폴백
```

- **캐시 우선**: 이미 이동한 경로를 바로 재사용, 연산 불필요
- **Baritone 통합**: 커뮤니티 최강 경로 탐색 엔진, 자동 굴기/다리 놓기/수영/용암 회피
- **건축 보호 구역 주입**: 기억된 건축물이 자동으로 Baritone 제외 영역에 주입
- **자동 학습**: 매번 내비게이션 결과가 기억 시스템에 자동 기록

### 🤖 이중 Agent 아키텍처 — 채팅과 작업 격리 (v2.0 신규)

```
메인 Agent:   채팅 담당, 영속적 컨텍스트, 의도 파악만 수행 (~50 Token/회)
작업 Agent:   실행 담당, 상태 없이 매번 새 컨텍스트 (<1500 Token/회)
```

- **메인 Agent**: 대화 컨텍스트를 유지하며 `[TASK:xxx]` 태그를 인식
- **작업 Agent**: 상태 비저장, 사용 후 폐기, 컨텍스트 폭발 방지
- **기억 주입**: AI 의사결정 시 기억 컨텍스트를 자동 주입 (건축 보호 구역, 알려진 경로 등)

### 🔌 Fabric Mod 아키텍처 — 정밀하고 안정적

- **프로토콜 파싱 불필요**: 게임 내부 API를 직접 호출
- **13개 HTTP 엔드포인트** + WebSocket 실시간 이벤트
- **Baritone 선택적 통합**: 있으면 고급 경로 탐색, 없으면 기본 직선 이동

### 🛡️ 5단계 보안 체계

| 등급 | 이름 | 예시 | 전략 |
|------|------|------|------|
| 0 | 완전 안전 | 이동, 점프 | 자동 실행 |
| 1 | 저위험 | 흙 캐기, 횃불 설치 | 자동 실행 |
| 2 | 중위험 | 광석 캐기, 중립 생물 공격 | 자동 실행 |
| 3 | 고위험 | TNT 점화, 용암 배치 | 플레이어 승인 필요 |
| 4 | 치명적 위험 | 명령 블록 배치 | 기본적으로 금지 |

---

## 🏗️ 시스템 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                    Minecraft 서버                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            BlockMind Fabric Mod (Java)                 │  │
│  │                                                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │상태 수집기│ │동작 실행기│ │이벤트 리스너│ │Baritone  │ │  │
│  │  │블록/엔티티│ │이동/채굴/ │ │채팅/피해/ │ │경로 탐색 │ │  │
│  │  │인벤토리/ │ │배치/공격 │ │블록 변화  │ │엔진(선택)│ │  │
│  │  │월드     │ │          │ │          │ │          │ │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │  │
│  │       └─────────────┼────────────┼────────────┘       │  │
│  │               HTTP API :25580 + WebSocket              │  │
│  └─────────────────────────────┼──────────────────────────┘  │
└────────────────────────────────┼─────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────┐
│                  BlockMind Python 백엔드                      │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   이중 Agent 아키텍처                   │  │
│  │  ┌─────────────────┐  ┌────────────────────────────┐  │  │
│  │  │ 메인 Agent (채팅) │  │ 작업 Agent (실행, 무상태)   │  │  │
│  │  │ 영속적 컨텍스트   │  │ 매번 새 컨텍스트           │  │  │
│  │  │ 의도 파악        │  │ Skill 매칭/생성/실행       │  │  │
│  │  └────────┬────────┘  └─────────────┬──────────────┘  │  │
│  └───────────┼─────────────────────────┼─────────────────┘  │
│              │                         │                     │
│  ┌───────────▼─────────────────────────▼─────────────────┐  │
│  │               🧠 기억 시스템 (GameMemory)              │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │공간 기억 │ │경로 기억 │ │전략 기억 │ │플레이어  │ │  │
│  │  │건축 보호 │ │성공 경로 │ │성공 전략 │ │기억     │ │  │
│  │  │구역     │ │캐시     │ │축적     │ │집 위치  │ │  │
│  │  │위험 지역│ │실패     │ │실패 기록│ │선호 습관│ │  │
│  │  │자원 광맥│ │블랙리스트│ │컨텍스트│ │상호작용 │ │  │
│  │  │         │ │성공률   │ │태그    │ │기록    │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │  │
│  │              영속화 JSON (data/memory/)                │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │ 주입                          │
│  ┌──────────┐ ┌──────────────▼──────┐ ┌──────────────────┐  │
│  │Skill 엔진│ │ 지능형 내비게이션   │ │ AI 의사결정 계층  │  │
│  │DSL 파싱  │ │ 기억→캐시→Baritone  │ │ 기억 컨텍스트 주입│  │
│  │매칭 실행 │ │ →A* 폴백→자동 학습  │ │ provider.py      │  │
│  └──────────┘ └─────────────────────┘ └──────────────────┘  │
│  ┌──────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │보안 검증 │ │ 헬스 모니터링│ │ WebUI (Miuix Console)   │ │
│  │5단계 위험│ │ 3단계 폴백   │ │ 다크 테마/모델 설정    │ │
│  │관리      │ │              │ │                         │ │
│  └──────────┘ └──────────────┘ └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### 데이터 흐름 예시

**기억 기반 지능형 내비게이션:**
```
플레이어가 "집에 가줘"라고 말함
  → 메인 Agent가 작업 인식 [TASK:집에 가기]
  → 작업 Agent가 go_home Skill 매칭
  → SmartNavigator가 기억 조회:
      ✅ 집 위치: (65, 64, -120) — 플레이어 기억에서 가져옴
      ✅ 캐시된 경로: 3회 이동, 성공률 100%
      ✅ 건축 보호 구역: 기지 주변 30블록 파괴 금지
      ✅ 위험 지역: (80,12,-50) 용암 존재
  → Baritone 내비게이션:
      GoalBlock(65, 64, -120)
      + exclusion_zones=[기지 보호 구역]
      → 자동 우회, 건물 파괴 없음
  → 도착 후: 경로 캐시 success_count+1
  → 다음 귀환: 캐시된 경로를 바로 사용, Token 소비 0
```

---

## 🧠 기억 시스템

### 3계층 기억 아키텍처

| 계층 | 저장 내용 | 영속화 | 예시 |
|------|----------|--------|------|
| **공간 기억** | 건축 보호 구역, 위험 지역, 자원 포인트, 기지 | ✅ JSON | "기지 범위: (50-100, 60-80, -150--90)" |
| **경로 기억** | 성공 경로 캐시, 실패 경로 블랙리스트, 성공률 | ✅ JSON | "집→광산: (70,64,-100) 경유 성공률 100%" |
| **전략 기억** | 성공 전략 축적, 실패 교훈, 컨텍스트 태그 | ✅ JSON | "광석 채굴 시 횃불을 먼저 놓고 캐는 것이 효율 최대" |
| **플레이어 기억** | 집 위치, 선호 도구, 상호작용 기록 | ✅ JSON | "Steve의 집은 (100,64,200)" |
| **월드 기억** | 스폰 지점, 안전 지점, 중요 이벤트 | ✅ JSON | "스폰 지점 (0,64,0), 안전 지점 목록" |

### 자동 건축 보호

```python
# 건축 보호 구역 등록 (AI 파괴 금지)
memory.register_building("주성", center=(100, 64, 200), radius=30)
# → 내비게이션 시 자동으로 Baritone exclusion_zones에 주입
# → type: "no_break" + "no_place"
# → AI는 보호 구역 내에서 블록을 파괴/배치할 수 없음

# 자동 감지 (60초마다 주변 스캔)
navigator.auto_detect_and_memorize()
# → 연속된 건축 블록 감지 → 자동으로 보호 구역으로 등록
# → 용암/불꽃 감지 → 자동으로 위험 지역으로 등록
# → 광석 밀집 감지 → 자동으로 자원 포인트로 등록
```

### 경로 캐싱 메커니즘

```python
# 첫 번째 내비게이션: AI 계획 + 실행
result = await navigator.goto(100, 64, 200)
# → 경로 캐싱: success_count=1, success_rate=100%

# 두 번째 내비게이션: 캐시된 경로 바로 사용
result = await navigator.goto(100, 64, 200)
# → 캐시 경로 히트, 바로 실행, 연산 불필요

# 실패 경로: 자동 학습
# → fail_count >= 3 → 자동으로 블랙리스트에 추가
# → 다음번에 새 경로를 계획, 이전 경로 사용 안 함
```

### 전략 자동 축적

```python
# 작업 Agent 실행 성공 후 자동 기록
memory.record_strategy(
    task_type="mine",
    description="횃불을 먼저 놓고 광석 캐기",
    action_sequence=[...],
    success=True,
    context_tags=["nighttime", "cave"],
)

# 같은 작업 유형일 때 최적 전략 자동 매칭
best = memory.get_best_strategy("mine", context_tags=["nighttime"])
# → 성공률이 가장 높은 전략 반환
```

### AI 기억 컨텍스트 주입

```python
# AI 의사결정 시마다 기억 자동 주입
memory_context = memory.get_ai_context()
# 출력:
# [기억 시스템]
# 기지:
#   - 집: (50, 64, -100) (반경 30)
# 건축 보호 구역 (파괴 금지):
#   - 주성: (100, 64, 200) (반경 20)
# 위험 지역:
#   - 용암호: (80, 12, -50) (lava)
# 알려진 신뢰할 수 있는 경로: 3개
# 검증된 전략: 5개
```

---

## 🛤️ 지능형 내비게이션

### 내비게이션 흐름

```
SmartNavigator.goto(x, y, z)
  │
  ├── 1. 안전 검사
  │     └── 목표가 보호 구역 내? → 경고하지만 거부하지 않음
  │
  ├── 2. 캐시된 경로 조회
  │     └── 신뢰할 수 있는 캐시가 있는가? → 캐시된 경로 바로 실행
  │
  ├── 3. 내비게이션 컨텍스트 확보
  │     ├── 제외 영역 (건축 보호 구역)
  │     ├── 위험 지역 (용암, 절벽)
  │     └── 신뢰할 수 있는 경로 참조
  │
  ├── 4. Baritone 경로 탐색 (우선)
  │     ├── exclusion_zones 주입
  │     ├── 자동 굴기 / 다리 놓기 / 수영
  │     └── 낙하 비용 / 용암 회피
  │
  ├── 5. A* 경로 탐색 (폴백)
  │     └── 기본 그리드 A* + 블록 통행 가능 여부 판단
  │
  └── 6. 결과 기록
        ├── 성공 → cache_path(success=True)
        └── 실패 → cache_path(success=False) + 블랙리스트 가능성
```

### Baritone 통합

| 기능 | Baritone | 기본 A* |
|------|----------|---------|
| 경로 탐색 알고리즘 | 개선된 A* + 비용 휴리스틱 | 표준 A* |
| 굴기 | ✅ 장애물 자동 굴파 | ❌ |
| 다리 놓기 | ✅ 스캐폴드 모드 | ❌ |
| 수영 | ✅ | ❌ |
| 수직 이동 | ✅ 점프/사다리/덩굴 | ⚠️ 1블록만 |
| 용암 회피 | ✅ 비용 패널티 | ❌ |
| 낙하 비용 | ✅ 휴리스틱 함수에 포함 | ❌ |
| 제외 영역 | ✅ `exclusionAreas` | ❌ |
| **건축 보호** | ✅ `no_break` 영역 주입 | ❌ |

### 제외 영역 유형

| 유형 | 설명 | 출처 |
|------|------|------|
| `no_break` | 블록 파괴 금지 | 건축 보호 구역, 기지 |
| `no_place` | 블록 배치 금지 | 건축 보호 구역 |
| `avoid` | 완전 우회 | 위험 지역 (용암 등) |

---

## 🤖 이중 Agent 아키텍처

### 왜 이중 Agent가 필요한가?

```
단일 Agent의 문제:
  채팅 컨텍스트 + 작업 컨텍스트 → Token 폭발 (>4000/회)
  작업 실패가 채팅을 오염 → 대화 경험 저하
  매번 작업할 때마다 전체 채팅 기록을 포함 → 낭비

이중 Agent 방안:
  메인 Agent: 채팅만 담당, 슬라이딩 윈도우 20개, ~50 Token/회
  작업 Agent: 무상태, 매번 새 컨텍스트, <1500 Token/회
```

### 흐름

```
플레이어 메시지
  → 메인 Agent 채팅 (영속적 컨텍스트)
  → [TASK:xxx] 태그 인식
  → 작업 설명 추출
  → 작업 Agent 실행 (무상태):
      ├── Skill 매칭 조회
      ├── 기억 컨텍스트 주입
      ├── L1/L2: 캐시된 Skill 실행
      ├── L3: AI가 템플릿 채우기 + 실행
      └── L4: AI가 완전 추론 + 실행
  → 메인 Agent가 응답 포맷팅 → 플레이어
```

---
## 🚀 빠른 시작

### 환경 요구사항

| 구성 요소 | 요구사항 |
|----------|----------|
| Python | 3.10+ |
| Java | 17+ |
| Minecraft | 1.19.4 - 1.21.4 |
| Fabric Loader | 0.15+ |

---

## 📦 원클릭 배포

### 다운로드

[GitHub Releases](https://github.com/bmbxwbh/BlockMind/releases/latest)에서 다운로드:

| 파일 | 설명 |
|------|------|
| `blockmind-mod-1.0.0.jar` | Fabric Mod (서버 mods/ 폴더에 배치) |
| `Source code` (zip/tar) | 전체 소스 코드 |

### Linux / macOS 원클릭 시작

```bash
# 클론
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

# 원클릭 시작 (자동으로 의존성 설치 + MC 서버 + BlockMind + WebUI)
chmod +x start.sh
./start.sh
```

> `start.sh`가 자동으로: Python/Java 감지 → 의존성 설치 → 기존 MC 서버 스캔 → 버전 선택 설치 → 전체 시작

### Windows 원클릭 시작

```cmd
:: 클론 (또는 zip 다운로드 후 압축 해제)
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

:: 원클릭 설치
install.bat

:: 원클릭 시작 (MC 서버 + BlockMind + WebUI)
start_all.bat
```

> 자세한 단계는 [Windows 배포 가이드](docs/WINDOWS.md)를 참조하세요.

### Docker 배포

```bash
# 이미지 풀
docker pull ghcr.io/bmbxwbh/blockmind:latest

# 설정 템플릿 다운로드
wget https://raw.githubusercontent.com/bmbxwbh/BlockMind/main/config.example.yaml -O config.yaml
# config.yaml를 편집하여 AI 모델 설정을 입력하세요

# 시작
docker run -d \
  --name blockmind \
  -p 19951:19951 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v blockmind-data:/data \
  ghcr.io/bmbxwbh/blockmind:latest
```

또는 docker-compose 사용:

```bash
git clone https://github.com/bmbxwbh/BlockMind.git && cd BlockMind
cp config.example.yaml config.yaml
# config.yaml 편집
docker compose up -d
```

```bash
# 로그 확인
docker compose logs -f blockmind
# 중지
docker compose down
```

### 설정

`config.yaml` 편집:

```yaml
ai:
  main_agent:
    provider: "openai"          # openai 또는 anthropic
    api_key: "sk-your-key"
    model: "gpt-4o"             # 사용할 모델명
    base_url: ""                # 커스텀 API 주소 (선택)

webui:
  enabled: true
  port: 19951
  auth:
    password: "your-password"   # WebUI 로그인 비밀번호
```

시작 후 `http://localhost:19951`에 접속하여 제어 패널을 이용하세요.

---

## 🔌 Fabric Mod API

### 상태 조회

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/health` | GET | 헬스 체크 |
| `/api/status` | GET | 플레이어 상태 |
| `/api/world` | GET | 월드 상태 |
| `/api/inventory` | GET | 인벤토리 정보 |
| `/api/entities?radius=32` | GET | 주변 엔티티 |
| `/api/blocks?radius=16` | GET | 주변 블록 |

### 동작 실행

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/move` | POST | 좌표로 이동 |
| `/api/dig` | POST | 블록 채굴 |
| `/api/place` | POST | 블록 배치 |
| `/api/attack` | POST | 엔티티 공격 |
| `/api/eat` | POST | 식사 |
| `/api/look` | POST | 좌표 바라보기 |
| `/api/chat` | POST | 채팅 전송 |

### 경로 계획

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/pathfind` | POST | 경로 내비게이션 (Baritone/A*) |
| `/api/pathfind/stop` | POST | 내비게이션 중지 |
| `/api/pathfind/status` | GET | 내비게이션 상태 |

### 이벤트 푸시

Mod가 WebSocket으로 이벤트를 푸시합니다:
- `player_damaged` — 플레이어 피해
- `entity_attack` — 피격
- `health_low` — 체력 낮음
- `inventory_full` — 인벤토리 가득 참
- `block_broken` — 블록 채굴 완료

---

## 📝 Skill DSL 시스템

### 작업 분류

| 등급 | 유형 | 예시 | 캐싱 전략 |
|------|------|------|----------|
| L1 | 고정 작업 | "집에 가기" | 바로 실행 |
| L2 | 매개변수화 작업 | "다이아몬드 10개 캐기" | 매개변수 포함 캐싱 |
| L3 | 템플릿 작업 | "은신처 하나 짓기" | 템플릿 매칭 |
| L4 | 동적 작업 | "엔더 드래곤을 물리쳐 줘" | AI 추론 |

### Skill YAML 예시

```yaml
skill_id: mine_diamonds
name: "다이아몬드 채굴"
level: L2
parameters:
  count: {type: int, default: 10, min: 1, max: 64}
steps:
  - action: pathfind
    target: {y: -59}
    note: "다이아몬드 층으로 이동"
  - action: dig_loop
    block: diamond_ore
    count: ${count}
  - action: pathfind
    target: home
    note: "기지로 복귀"
```

---

## 🛡️ 보안 체계

| 계층 | 메커니즘 | 설명 |
|------|----------|------|
| L1 | 위험 평가 | 각 동작에 0-100점 부여 |
| L2 | 작업 승인 | 고위험 시 확인 필요 |
| L3 | 긴급 인수 | 플레이어가 언제든 AI를 중단 가능 |
| L4 | 감사 로그 | 모든 작업 추적 가능 |
| L5 | 안전 구역 제한 | 파괴/배치 범위 제한 |

---

## 🖥️ WebUI 제어 패널

시작 후 `http://localhost:19951`에 접속하면 다음을 지원합니다:

- 📊 대시보드 — 실시간 상태 모니터링
- 🛠️ Skill 관리 — 온라인 YAML 편집
- 🧠 기억 시스템 — 조회/정리/백업
- 🤖 모델 설정 — AI 모델 핫스위칭
- 💬 명령 패널 — 자연어 명령
- 📋 작업 대기열 — 실행 상태 확인
- 📝 로그 센터 — 실시간 로그 스트림

---

## ❓ FAQ

**Q: Baritone를 반드시 설치해야 하나요?**
A: 아닙니다. Baritone는 선택적 의존성이며, 없을 경우 기본 A* 직선 이동으로 자동 폴백됩니다.

**Q: 기억 데이터는 어디에 저장되나요?**
A: `data/memory/` 디렉토리 아래에 5개 JSON 파일로 세션 간 보존됩니다.

**Q: 건축 보호는 어떻게 적용되나요?**
A: 두 가지 방법이 있습니다: ① 수동 등록 ② 자동 감지 (60초마다 스캔).

**Q: 어떤 AI 제공자를 지원하나요?**
A: OpenAI 호환 형식 (DeepSeek/OpenRouter/MiMo 등 포함) + Anthropic 형식.

**Q: Docker 이미지 용량은 얼마나 되나요?**
A: 약 200MB이며, python:3.11-slim 기반 다단계 빌드입니다.

---

## 🗺️ 로드맵

### v3.0 (현재) ✅
- [x] 3계층 기억 시스템 (공간/경로/전략)
- [x] 지능형 내비게이션 (기억 기반 + Baritone 통합)
- [x] 이중 Agent 아키텍처 (채팅/작업 격리)
- [x] 건축 보호 구역 자동 보호
- [x] Miuix Console WebUI
- [x] Windows/Linux 원클릭 배포
- [x] Docker 이미지 + GHCR 자동 배포
- [x] GitHub Actions CI/CD

### v3.1 (계획 중)
- [ ] 멀티모달 입력 (스크린샷 분석)
- [ ] Skill 마켓플레이스 (가져오기/내보내기)
- [ ] 다중 플레이어 협동
- [ ] 음성 상호작용

---

## 📄 라이선스

MIT License. 자세한 내용은 [LICENSE](LICENSE)를 참조하세요.
