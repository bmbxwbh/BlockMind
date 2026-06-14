# 🧠 BlockMind

> **Fabric Mod + AI + sistem memori** · Teman AI Minecraft yang cerdas

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![MC](https://img.shields.io/badge/Minecraft-1.20~26.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT--NC-purple.svg)](LICENSE)

Fabric Mod menyediakan antarmuka game presisi + Python menggerakkan keputusan AI + sistem memori belajar lintas sesi. **Mendukung mode server dan client**, bisa digunakan di game solo, LAN, atau server.

🌐 [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | **Bahasa Indonesia**

---

## Mengapa BlockMind

### 1. Sistem memori — AI belajar

Teman AI tradisional melupakan semua saat restart. BlockMind memiliki tiga lapis memori permanen:

- **Memori ruang**: Secara otomatis mengingat zona perlindungan bangunan, area berbahaya, titik sumber daya
- **Memori jalur**: Menyimpan jalur sukses, memblacklist jalur gagal
- **Memori strategi**: Operasi sukses menjadi strategi yang dapat digunakan ulang Zero Token

AI secara otomatis menghindari bangunan pemain saat navigasi, tidak pernah merusak rumah.

### 2. Arsitektur Dual Agent — Hemat Token

```
Agent Utama (~50 Token/kali): hanya chat + pengenalan niat
Agent Operasi (<1500 Token/kali): stateless, sekali pakai
```

Dibanding Single Agent (>4000 Token/kali), hemat 84%.

### 3. Mode Server dan Client

| Mode | Lokasi instalasi | Pemain | Skenario |
|------|-----------------|--------|----------|
| Server | `mods/` di server | FakePlayer (bot) | Server 7×24 |
| Client | `mods/` di client | Pemain lokal | Game solo / LAN |

### 4. Baritone + perlindungan bangunan

AI menggunakan Baritone untuk navigasi (menggali/membangun jembatan/berenang) tetapi secara otomatis menghindari zona perlindungan bangunan. Bangunan yang tercatat di memori diinjeksi sebagai zona eksklusi Baritone.

### 5. Skill DSL + marketplace

Mendefinisikan keterampilan AI yang dapat digunakan ulang menggunakan YAML (menambang, bertani, membangun), berbagi komunitas. Skill yang dibuat AI otomatis tersimpan dan dieksekusi dengan Zero Token.

---

## Memulai cepat

### Persyaratan

- Python 3.10+ · Java 17+ · Minecraft 1.20.0 ~ 26.1.2

### Memulai

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

### Konfigurasi

Edit `config.yaml`:

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

Setelah memulai, akses `http://localhost:19951` untuk masuk ke panel kontrol.

---

## Arsitektur

```
┌──────────────── Minecraft ────────────────┐
│  BlockMind Fabric Mod (Java)              │
│  Pengumpulan status · Eksekusi aksi       │
│  HTTP API :25580 · WebSocket              │
└──────────────────┬────────────────────────┘
                   │
┌──────────────────▼────────────────────────┐
│  BlockMind Python Backend                 │
│  ┌──────────┐  ┌──────────────────────┐  │
│  │ Agent    │  │ Agent Operasi        │  │
│  │ Utama    │  │ (stateless)          │  │
│  │ Chat     │  │ Pencocokan/          │  │
│  └─────┬────┘  └──────────┬───────────┘  │
│  ┌─────▼──────────────────▼───────────┐  │
│  │ Memori · Navigasi · Skill          │  │
│  └────────────────┬───────────────────┘  │
│  ┌────────────────▼───────────────────┐  │
│  │ WebUI (MiuiX)                      │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## WebUI

`http://localhost:19951` — Ikon Lucide + tema gelap MiuiX

| Fitur | Keterangan |
|-------|-----------|
| Dashboard | Status real-time, perintah cepat, aliran peristiwa |
| Manajemen Skill | Edit YAML online, eksekusi sekali klik |
| Marketplace Skill | Skill komunitas, instal, impor/ekspor |
| Sistem Memori | Lihat/backup/bersihkan/impor/ekspor |
| Konfigurasi Model | Pengaturan Dual Agent, pergantian panas |
| Pengaturan Keamanan | Tingkat risiko, log audit |
| Antrian Tugas | Pemantauan status eksekusi |
| Pusat Log | Aliran log WebSocket real-time |

---

## Ringkasan API

| Endpoint | Metode | Keterangan |
|----------|--------|-----------|
| `/api/status` | GET | Status pemain |
| `/api/inventory` | GET | Informasi inventaris |
| `/api/entities` | GET | Entitas di sekitar |
| `/api/move` | POST | Bergerak ke koordinat |
| `/api/dig` | POST | Menggali blok |
| `/api/place` | POST | Menaruh blok |
| `/api/attack` | POST | Menyerang entitas |
| `/api/chat` | POST | Mengirim chat |

Dokumentasi lengkap: [Fabric Mod API](docs/MOD_BUILD.md)

---

## Versi yang didukung

| MC versi | Java | Status |
|----------|------|--------|
| 1.20.0 ~ 1.20.6 | 17~21 | ✅ |
| 1.21 ~ 1.21.4 | 21 | ✅ |
| 26.1 ~ 26.1.2 | 25 | ✅ Terbaru |

---

## FAQ

**Q: Harus pasang Baritone?** Tidak wajib, tanpa itu pakai A* dasar.

**Q: Data memori disimpan di mana?** Di `data/memory/`, 5 file JSON.

**Q: Provider AI apa yang didukung?** Format OpenAI (DeepSeek/OpenRouter/MiMo) + Anthropic.

**Q: Bisa dipakai di game solo?** Bisa, letakkan Mod di `mods/` client.

---

## Lisensi

MIT-NC — penggunaan komersial dilarang. Detail: [LICENSE](LICENSE).
