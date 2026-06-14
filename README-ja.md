# 🧠 BlockMind

> **Fabric Mod + AI + 記憶システム** · Minecraft AI コンパニオン

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![MC](https://img.shields.io/badge/Minecraft-1.20~26.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT--NC-purple.svg)](LICENSE)

Fabric Mod が精密なゲームインターフェースを提供し、Python バックエンドが AI 意思決定を駆動、記憶システムがセッション間学習を実現。**サーバーとクライアントの両モードをサポート** — シングルプレイ、LAN、サーバーで使用可能。

🌐 [中文](README.md) | [English](README-en.md) | **日本語** | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | [Español](README-es.md) | [Français](README-fr.md)

---

## なぜ BlockMind なのか

### 1. 記憶システム — 学習する AI

従来の AI コンパニオンは再起動のたびに全て忘れる。BlockMind は3層の永続記憶を持つ：

- **空間記憶**: 建築保護区域、危険エリア、資源ポイントを自動記憶
- **パス記憶**: 成功パスをキャッシュ、失敗パスをブラックリスト化、次回はそのまま再利用
- **戦略記憶**: 成功操作を自動的に再利用可能な戦略として蓄積、Token 消費ゼロ

ナビゲーション時にプレイヤー建築を自動回避、基地を破壊することはない。

### 2. デュアル Agent アーキテクチャ — Token 削減

```
メイン Agent（~50 Token/回）: チャット + 意図識別のみ
操作 Agent（<1500 Token/回）: ステートレス、使い捨て実行
```

単一 Agent 方案（>4000 Token/回）と比較して、84% のコスト削減。

### 3. サーバー + クライアント デュアルモード

| モード | インストール先 | プレイヤー | シナリオ |
|--------|---------------|-----------|---------|
| サーバー | サーバー `mods/` | FakePlayer (Bot) | サーバー 7×24 時間放置 |
| クライアント | クライアント `mods/` | ローカルプレイヤー | シングルプレイ / LAN |

### 4. Baritone 統合 + 建築保護

AI は Baritone で経路探索（自動掘削/架橋/泳行）を行うが、建築保護区域を自動的に迂回。記憶された建築物はリアルタイムで Baritone の除外区域に注入される。

### 5. Skill DSL + マーケットプレイス

YAML で再利用可能な AI スキル（採掘、農耕、建築）を定義し、コミュニティと共有。AI が生成したスキルは自動保存、次回実行時に Token 消費ゼロ。

---

## クイックスタート

### 環境要件

- Python 3.10+ · Java 17+ · Minecraft 1.20.0 ~ 26.1.2

### ワンクリック起動

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

### 設定

`config.yaml` を編集：

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

起動後 `http://localhost:19951` でコントロールパネルにアクセス。

---

## アーキテクチャ

```
┌──────────────── Minecraft ────────────────┐
│  BlockMind Fabric Mod (Java)              │
│  状態収集 · アクション実行                 │
│  イベントリスニング                        │
│  HTTP API :25580 · WebSocket              │
└──────────────────┬────────────────────────┘
                   │
┌──────────────────▼────────────────────────┐
│  BlockMind Python バックエンド              │
│  ┌──────────┐  ┌──────────────────────┐  │
│  │ メイン   │  │ 操作 Agent           │  │
│  │ Agent    │  │ (ステートレス)       │  │
│  │ チャット+ │  │ Skill マッチ/生成/   │  │
│  │ 識別     │  │ 実行                 │  │
│  └─────┬────┘  └──────────┬───────────┘  │
│  ┌─────▼──────────────────▼───────────┐  │
│  │ 記憶システム · インテリジェントナビ  │  │
│  │ · Skill エンジン                   │  │
│  └────────────────┬───────────────────┘  │
│  ┌────────────────▼───────────────────┐  │
│  │ WebUI コントロールパネル (MiuiX)   │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## WebUI コントロールパネル

`http://localhost:19951` — Lucide アイコン + MiuiX ダークテーマ

| 機能 | 説明 |
|------|------|
| ダッシュボード | リアルタイム状態、クイックコマンド、イベントストリーム |
| Skill 管理 | オンライン YAML 編集、ワンクリック実行 |
| Skill マーケット | コミュニティスキルの閲覧、インストール、インポート/エクスポート |
| 記憶システム | 表示 / バックアップ / クリーンアップ / インポート/エクスポート |
| モデル設定 | デュアル Agent モデル設定、ホットスイッチ |
| セキュリティ設定 | リスクレベル、監査ログ |
| タスクキュー | 実行状態の監視 |
| ログセンター | リアルタイム WebSocket ログストリーム |

---

## Fabric Mod API

| エンドポイント | メソッド | 説明 |
|----------------|----------|------|
| `/api/status` | GET | プレイヤー状態 |
| `/api/inventory` | GET | インベントリ情報 |
| `/api/entities` | GET | 周辺エンティティ |
| `/api/move` | POST | 座標へ移動 |
| `/api/dig` | POST | ブロック掘削 |
| `/api/place` | POST | ブロック設置 |
| `/api/attack` | POST | エンティティ攻撃 |
| `/api/chat` | POST | チャット送信 |

完全な API ドキュメント: [Fabric Mod API](docs/MOD_BUILD.md)。

---

## 対応バージョン

| MC バージョン | Java | 状態 |
|---------------|------|------|
| 1.20.0 ~ 1.20.6 | 17~21 | ✅ |
| 1.21 ~ 1.21.4 | 21 | ✅ |
| 26.1 ~ 26.1.2 | 25 | ✅ 最新 |

---

## FAQ

**Q: Baritone は必須ですか？** いえ、不要です。ない場合は基本 A* にフォールバックします。

**Q: 記憶データはどこに保存されますか？** `data/memory/` ディレクトリの 5 つの JSON ファイルです。

**Q: どの AI モデルに対応していますか？** OpenAI 互換形式（DeepSeek/OpenRouter/MiMo）+ Anthropic。

**Q: シングルプレイで使用できますか？** はい、クライアントの `mods/` フォルダに Mod を入れるだけです。

---

## ライセンス

MIT-NC — 商用利用禁止。詳細は [LICENSE](LICENSE) を参照。
