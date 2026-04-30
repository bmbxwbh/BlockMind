# 🧠 BlockMind — Sistem Teman AI Minecraft yang Cerdas

> **Fabric Mod + Berbasis AI + Sistem Memori** · v3.0 · 2026-04-30

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![Fabric](https://img.shields.io/badge/Fabric-0.92+-yellow.svg)](https://fabricmc.net)
[![MC](https://img.shields.io/badge/Minecraft-1.20.x--1.21.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**Ringkasan dalam satu kalimat:** Fabric Mod menyediakan antarmuka permainan yang presisi + backend Python menggerakkan keputusan AI + sistem memori untuk pembelajaran lintas sesi, mewujudkan teman AI Minecraft yang mampu bertahan hidup secara otonom 7×24 jam.

🌐 [中文](README.md) | [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | [Español](README-es.md) | [Français](README-fr.md) | **Bahasa Indonesia** | [Italiano](README-it.md) | [Português](README-pt.md) | [Русский](README-ru.md) | [ภาษาไทย](README-th.md) | [Türkçe](README-tr.md) | [Tiếng Việt](README-vi.md)
---

## 📖 Daftar Isi

- [Keunggulan Proyek](#-keunggulan-proyek)
- [Arsitektur Sistem](#-arsitektur-sistem)
- [Sistem Memori](#-sistem-memori)
- [Navigasi Cerdas](#-navigasi-cerdas)
- [Arsitektur Dual Agent](#-arsitektur-dual-agent)
- [Memulai Cepat](#-memulai-cepat)
- [Deployment Sekali Klik](#-deployment-sekali-klik)
- [Fabric Mod API](#-fabric-mod-api)
- [Sistem Skill DSL](#-sistem-skill-dsl)
- [Sistem Keamanan](#-sistem-keamanan)
- [Panel Kontrol WebUI](#-panel-kontrol-webui)
- [Panduan Deployment](#-panduan-deployment)
- [FAQ](#faq)
- [Peta Jalan](#-peta-jalan)

---

## ✨ Keunggulan Proyek

### 🧠 Sistem Memori — Pembelajaran Lintas Sesi (v3.0 Baru)

```
Cara tradisional:  Lupa semua setiap restart, mengulangi kesalahan, membuang Token
Dengan memori:     Tiga lapis memori (ruang/jalur/strategi), persistensi JSON, lintas sesi
```

- **Memori Ruang**: Mendeteksi dan mengingat zona perlindungan bangunan, area berbahaya, titik sumber daya secara otomatis
- **Memori Jalur**: Mencache jalur sukses, memasukkan jalur gagal ke daftar hitam, statistik tingkat keberhasilan
- **Memori Strategi**: Operasi sukses secara otomatis terdistilasi menjadi strategi yang dapat digunakan ulang, nol Token untuk penggunaan ulang
- **Perlindungan Bangunan**: Secara otomatis menghindari bangunan pemain saat navigasi, tidak perlu khawatir rumah hancur

### 🛤️ Navigasi Cerdas — Pencarian Jalur Berbasis Memori (v3.0 Baru)

```
Cara tradisional:  walk_to(x,y,z) → Terhalang tembok / Menghancurkan bangunan
Navigasi cerdas:   Cek memori → Jalur cache → Baritone(zona eksklusi) → Fallback A*
```

- **Prioritas Cache**: Jalur yang sudah dilalui langsung digunakan ulang, nol komputasi
- **Integrasi Baritone**: Mesin pencari jalur terkuat dari komunitas, otomatis menggali/membangun jembatan/berenang/menghindari lava
- **Injeksi Zona Perlindungan**: Bangunan yang tercatat di memori otomatis diinjeksi sebagai zona eksklusi Baritone
- **Pembelajaran Otomatis**: Setiap hasil navigasi otomatis tercatat ke sistem memori

### 🤖 Arsitektur Dual Agent — Isolasi Chat dan Operasi (v2.0 Baru)

```
Agent Utama:   Bertanggung jawab atas chat, konteks persisten, hanya pengenalan niat (~50 Token/sekali)
Agent Operasi: Bertanggung jawab atas eksekusi, stateless, konteks baru setiap kali (<1500 Token/sekali)
```

- **Agent Utama**: Menjaga konteks percakapan, mengenali tag `[TASK:xxx]`
- **Agent Operasi**: Stateless, sekali pakai, menghindari ledakan konteks
- **Injeksi Memori**: Saat keputusan AI, konteks memori otomatis diinjeksi (zona perlindungan bangunan, jalur yang diketahui, dll.)

### 🔌 Arsitektur Fabric Mod — Presisi dan Andal

- **Nol Parsing Protokol**: Langsung memanggil API internal game
- **13 Endpoint HTTP** + peristiwa real-time WebSocket
- **Integrasi Baritone Opsional**: Jika ada → pencarian jalur lanjutan, jika tidak → garis lurus dasar

### 🛡️ Sistem Keamanan Lima Tingkat

| Tingkat | Nama | Contoh | Strategi |
|---------|------|--------|----------|
| 0 | Sepenuhnya aman | Bergerak, melompat | Eksekusi otomatis |
| 1 | Risiko rendah | Menggali tanah, memasang obor | Eksekusi otomatis |
| 2 | Risiko sedang | Menambang bijih, menyerang makhluk netral | Eksekusi otomatis |
| 3 | Risiko tinggi | Menyalakan TNT, menuangkan lava | Perlu otorisasi pemain |
| 4 | Risiko fatal | Memasang blok perintah | Dilarang secara default |

---

## 🏗️ Arsitektur Sistem

```
┌──────────────────────────────────────────────────────────────┐
│                    Minecraft Server                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            BlockMind Fabric Mod (Java)                 │  │
│  │                                                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Pengumpul │ │Pelaksana │ │Pendengar │ │Baritone  │ │  │
│  │  │Status    │ │Aksi      │ │Peristiwa │ │Mesin     │ │  │
│  │  │Blok/Enti │ │Bergerak/ │ │Chat/Cede │ │Navigasi  │ │  │
│  │  │tas/Tas/  │ │Menggali/ │ │ra/Blok   │ │(opsional)│ │  │
│  │  │Dunia     │ │Menaruh/  │ │berubah   │ │          │ │  │
│  │  │          │ │Menyerang │ │          │ │          │ │  │
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
│  │              Arsitektur Dual Agent                     │  │
│  │  ┌─────────────────┐  ┌────────────────────────────┐  │  │
│  │  │ Agent Utama     │  │ Agent Operasi              │  │  │
│  │  │ (Chat)          │  │ (Eksekusi, Stateless)      │  │  │
│  │  │ Konteks persisten│  │ Konteks baru setiap kali   │  │  │
│  │  │ Pengenalan niat │  │ Pencocokan/Generasi/       │  │  │
│  │  │                 │  │ Eksekusi Skill             │  │  │
│  │  └────────┬────────┘  └─────────────┬──────────────┘  │  │
│  └───────────┼─────────────────────────┼─────────────────┘  │
│              │                         │                     │
│  ┌───────────▼─────────────────────────▼─────────────────┐  │
│  │               🧠 Sistem Memori (GameMemory)            │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Memori    │ │Memori    │ │Memori    │ │Memori    │ │  │
│  │  │Ruang     │ │Jalur     │ │Strategi  │ │Pemain    │ │  │
│  │  │Zona      │ │Jalur     │ │Strategi  │ │Lokasi    │ │  │
│  │  │proteksi  │ │sukses    │ │sukses    │ │rumah     │ │  │
│  │  │Area      │ │Daftar    │ │Catatan   │ │Preferensi│ │  │
│  │  │berbahaya │ │hitam     │ │gagal     │ │kebiasaan │ │  │
│  │  │Titik     │ │Statistik │ │Tag       │ │Catatan   │ │  │
│  │  │sumber    │ │tingkat   │ │konteks   │ │interaksi │ │  │
│  │  │daya      │ │sukses    │ │          │ │          │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │  │
│  │              Persistensi JSON (data/memory/)            │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │ Injeksi                       │
│  ┌──────────┐ ┌──────────────▼──────┐ ┌──────────────────┐  │
│  │Mesin    │ │Navigasi Cerdas      │ │Lapisan Keputusan │  │
│  │Skill    │ │Memori→Cache→Baritone │ │AI                │  │
│  │Parsing  │ │→A* fallback→        │ │Injeksi konteks   │  │
│  │DSL      │ │Auto-learning        │ │memori            │  │
│  │Pencocokan│ │                    │ │provider.py       │  │
│  │Eksekusi │ │                    │ │                  │  │
│  └──────────┘ └─────────────────────┘ └──────────────────┘  │
│  ┌──────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │Validasi │ │Pemantauan   │ │ WebUI (Miuix Console)   │ │
│  │Keamanan │ │Kesehatan    │ │ Tema gelap/Konfigurasi  │ │
│  │5 tingkat│ │3 tingkat    │ │ model                   │ │
│  │risiko   │ │degradasi    │ │                         │ │
│  └──────────┘ └──────────────┘ └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Contoh Aliran Data

**Navigasi cerdas berbasis memori:**
```
Pemain mengatakan "pulang"
  → Agent Utama mengenali tugas [TASK:pulang]
  → Agent Operasi mencocokkan Skill go_home
  → SmartNavigator memeriksa memori:
      ✅ Lokasi rumah: (65, 64, -120) dari memori pemain
      ✅ Jalur cache: Sudah dilalui 3 kali, tingkat keberhasilan 100%
      ✅ Zona perlindungan bangunan: 30 blok di sekitar basis, dilarang merusak
      ✅ Area berbahaya: (80,12,-50) ada lava
  → Navigasi Baritone:
      GoalBlock(65, 64, -120)
      + exclusion_zones=[zona perlindungan basis]
      → Otomatis menghindari rintangan, tidak merusak bangunan apa pun
  → Setelah tiba: cache jalur success_count+1
  → Pulang berikutnya: langsung jalur cache, nol konsumsi Token
```

---

## 🧠 Sistem Memori

### Arsitektur Memori Tiga Lapis

| Lapis | Isi Penyimpanan | Persistensi | Contoh |
|-------|----------------|-------------|--------|
| **Memori Ruang** | Zona perlindungan bangunan, area berbahaya, titik sumber daya, basis | ✅ JSON | "Cakupan basis: (50-100, 60-80, -150--90)" |
| **Memori Jalur** | Cache jalur sukses, daftar hitam jalur gagal, tingkat keberhasilan | ✅ JSON | "Rumah→Gua tambang: via (70,64,-100) tingkat keberhasilan 100%" |
| **Memori Strategi** | Distilasi strategi sukses, pelajaran dari kegagalan, tag konteks | ✅ JSON | "Saat menambang, pasang obor dulu baru gali, paling efisien" |
| **Memori Pemain** | Lokasi rumah, alat preferensi, catatan interaksi | ✅ JSON | "Rumah Steve di (100,64,200)" |
| **Memori Dunia** | Titik spawn, titik aman, peristiwa penting | ✅ JSON | "Titik spawn (0,64,0), daftar titik aman" |

### Perlindungan Bangunan Otomatis

```python
# Mendaftarkan zona perlindungan bangunan (AI dilarang merusak)
memory.register_building("kota_pusat", center=(100, 64, 200), radius=30)
# → Saat navigasi otomatis diinjeksi ke Baritone exclusion_zones
# → type: "no_break" + "no_place"
# → AI di dalam zona perlindungan tidak bisa merusak/menaruh blok

# Deteksi otomatis (pindai sekitar setiap 60 detik)
navigator.auto_detect_and_memorize()
# → Terdeteksi blok bangunan berurutan → otomatis daftarkan sebagai zona perlindungan
# → Terdeteksi lava/api → otomatis daftarkan sebagai area berbahaya
# → Terdeteksi kumpulan bijih → otomatis daftarkan sebagai titik sumber daya
```

### Mekanisme Cache Jalur

```python
# Navigasi pertama: AI merencanakan + mengeksekusi
result = await navigator.goto(100, 64, 200)
# → Cache jalur: success_count=1, success_rate=100%

# Navigasi kedua: langsung jalur cache
result = await navigator.goto(100, 64, 200)
# → Cache hit, langsung eksekusi, nol komputasi

# Jalur gagal: pembelajaran otomatis
# → fail_count >= 3 → otomatis masuk daftar hitam
# → Lain kali rencanakan ulang, tidak jalan di rute lama
```

### Distilasi Strategi Otomatis

```python
# Setelah Agent Operasi berhasil mengeksekusi, otomatis catat
memory.record_strategy(
    task_type="mine",
    description="Pasang obor dulu baru menambang",
    action_sequence=[...],
    success=True,
    context_tags=["nighttime", "cave"],
)

# Lain kali tugas yang sama, otomatis cocokkan strategi terbaik
best = memory.get_best_strategy("mine", context_tags=["nighttime"])
# → Mengembalikan strategi dengan tingkat keberhasilan tertinggi
```

### Injeksi Konteks Memori AI

```python
# Setiap kali keputusan AI, memori otomatis diinjeksi
memory_context = memory.get_ai_context()
# Output:
# [Sistem Memori]
# Basis:
#   - Rumah: (50, 64, -100) (radius 30)
# Zona perlindungan bangunan (dilarang merusak):
#   - Kota pusat: (100, 64, 200) (radius 20)
# Area berbahaya:
#   - Danau lava: (80, 12, -50) (lava)
# Jalur terpercaya yang diketahui: 3 jalur
# Strategi terverifikasi: 5 strategi
```

---

## 🛤️ Navigasi Cerdas

### Alur Navigasi

```
SmartNavigator.goto(x, y, z)
  │
  ├── 1. Pemeriksaan keamanan
  │     └── Tujuan di dalam zona perlindungan? → Peringatan tapi tidak menolak
  │
  ├── 2. Pemeriksaan cache jalur
  │     └── Ada cache terpercaya? → Langsung eksekusi jalur cache
  │
  ├── 3. Mendapatkan konteks navigasi
  │     ├── Zona eksklusi (zona perlindungan bangunan)
  │     ├── Area berbahaya (lava, tebing)
  │     └── Referensi jalur terpercaya
  │
  ├── 4. Pencarian jalur Baritone (prioritas)
  │     ├── Injeksi exclusion_zones
  │     ├── Otomatis menggali/membangun jembatan/berenang
  │     └── Biaya jatuh / penghindaran lava
  │
  ├── 5. Pencarian jalur A* (fallback)
  │     └── A* grid dasar + penilaian keboleh-laluan blok
  │
  └── 6. Mencatat hasil
        ├── Sukses → cache_path(success=True)
        └── Gagal → cache_path(success=False) + kemungkinan daftar hitam
```

### Integrasi Baritone

| Fitur | Baritone | A* Dasar |
|-------|----------|----------|
| Algoritma pencarian jalur | A* yang ditingkatkan + heuristik biaya | A* standar |
| Menggali jalan | ✅ Otomatis menggali penghalang | ❌ |
| Membangun jembatan | ✅ Mode scaffold | ❌ |
| Berenang | ✅ | ❌ |
| Gerakan vertikal | ✅ Lompat/tangga/tanaman rambat | ⚠️ Hanya 1 blok |
| Penghindaran lava | ✅ Penalti biaya | ❌ |
| Biaya jatuh | ✅ Dihitung dalam fungsi heuristik | ❌ |
| Zona eksklusi | ✅ `exclusionAreas` | ❌ |
| **Perlindungan bangunan** | ✅ Injeksi zona `no_break` | ❌ |

### Tipe Zona Eksklusi

| Tipe | Keterangan | Sumber |
|------|-----------|--------|
| `no_break` | Dilarang merusak blok | Zona perlindungan bangunan, basis |
| `no_place` | Dilarang menaruh blok | Zona perlindungan bangunan |
| `avoid` | Sepenuhnya dihindari | Area berbahaya (lava, dll.) |

---

## 🤖 Arsitektur Dual Agent

### Mengapa Perlu Dual Agent?

```
Masalah Single Agent:
  Konteks chat + konteks operasi → Token meledak (>4000/sekali)
  Operasi gagal mencemari chat → Pengalaman percakapan buruk
  Setiap operasi harus membawa riwayat chat lengkap → Pemborosan

Solusi Dual Agent:
  Agent Utama: Hanya chat, jendela geser 20 pesan, ~50 Token/sekali
  Agent Operasi: Stateless, konteks baru setiap kali, <1500 Token/sekali
```

### Alur

```
Pesan pemain
  → Agent Utama mengobrol (konteks persisten)
  → Terdeteksi tag [TASK:xxx]
  → Ekstrak deskripsi tugas
  → Agent Operasi mengeksekusi (stateless):
      ├── Pencocokan Skill
      ├── Injeksi konteks memori
      ├── L1/L2: Eksekusi Skill cache
      ├── L3: AI mengisi template + eksekusi
      └── L4: AI reasoning penuh + eksekusi
  → Agent Utama memformat balasan → Pemain
```

---
## 🚀 Memulai Cepat

### Persyaratan Lingkungan

| Komponen | Persyaratan |
|----------|------------|
| Python | 3.10+ |
| Java | 17+ |
| Minecraft | 1.19.4 - 1.21.4 |
| Fabric Loader | 0.15+ |

---

## 📦 Deployment Sekali Klik

### Unduh

Unduh dari [GitHub Releases](https://github.com/bmbxwbh/BlockMind/releases/latest):

| File | Keterangan |
|------|-----------|
| `blockmind-mod-1.0.0.jar` | Fabric Mod (letakkan di folder mods/ server) |
| `Source code` (zip/tar) | Kode sumber lengkap |

### Linux / macOS Sekali Klik

```bash
# Clone
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

# Mulai sekali klik (otomatis instal dependensi + server MC + BlockMind + WebUI)
chmod +x start.sh
./start.sh
```

> `start.sh` otomatis: deteksi Python/Java → instal dependensi → pindai server MC yang ada → pilih versi instal → jalankan semua

### Windows Sekali Klik

```cmd
:: Clone (atau unduh zip dan ekstrak)
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

:: Instal sekali klik
install.bat

:: Mulai sekali klik (server MC + BlockMind + WebUI)
start_all.bat
```

> Langkah detail lihat [Panduan Deployment Windows](docs/WINDOWS.md)

### Deployment Docker

```bash
# Tarik image
docker pull ghcr.io/bmbxwbh/blockmind:latest

# Unduh template konfigurasi
wget https://raw.githubusercontent.com/bmbxwbh/BlockMind/main/config.example.yaml -O config.yaml
# Edit config.yaml, isi konfigurasi model AI Anda

# Jalankan
docker run -d \
  --name blockmind \
  -p 19951:19951 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v blockmind-data:/data \
  ghcr.io/bmbxwbh/blockmind:latest
```

Atau gunakan docker-compose:

```bash
git clone https://github.com/bmbxwbh/BlockMind.git && cd BlockMind
cp config.example.yaml config.yaml
# Edit config.yaml
docker compose up -d
```

```bash
# Lihat log
docker compose logs -f blockmind
# Hentikan
docker compose down
```

### Konfigurasi

Edit `config.yaml`:

```yaml
ai:
  main_agent:
    provider: "openai"          # openai atau anthropic
    api_key: "sk-your-key"
    model: "gpt-4o"             # Nama model Anda
    base_url: ""                # Alamat API kustom (opsional)

webui:
  enabled: true
  port: 19951
  auth:
    password: "your-password"   # Kata sandi login WebUI
```

Setelah mulai, akses `http://localhost:19951` untuk masuk ke panel kontrol.

---

## 🔌 Fabric Mod API

### Status Query

| Endpoint | Metode | Keterangan |
|----------|--------|-----------|
| `/health` | GET | Pemeriksaan kesehatan |
| `/api/status` | GET | Status pemain |
| `/api/world` | GET | Status dunia |
| `/api/inventory` | GET | Informasi tas/inventaris |
| `/api/entities?radius=32` | GET | Entitas di sekitar |
| `/api/blocks?radius=16` | GET | Blok di sekitar |

### Eksekusi Aksi

| Endpoint | Metode | Keterangan |
|----------|--------|-----------|
| `/api/move` | POST | Bergerak ke koordinat |
| `/api/dig` | POST | Menggali blok |
| `/api/place` | POST | Menaruh blok |
| `/api/attack` | POST | Menyerang entitas |
| `/api/eat` | POST | Makan |
| `/api/look` | POST | Melihat ke koordinat |
| `/api/chat` | POST | Mengirim chat |

### Perencanaan Jalur

| Endpoint | Metode | Keterangan |
|----------|--------|-----------|
| `/api/pathfind` | POST | Navigasi jalur (Baritone/A*) |
| `/api/pathfind/stop` | POST | Hentikan navigasi |
| `/api/pathfind/status` | GET | Status navigasi |

### Push Peristiwa

Mod mengirimkan peristiwa melalui WebSocket:
- `player_damaged` — Pemain terluka
- `entity_attack` — Diserang
- `health_low` — Darah rendah
- `inventory_full` — Tas/inventaris penuh
- `block_broken` — Penggalian blok selesai

---

## 📝 Sistem Skill DSL

### Tingkatan Tugas

| Tingkat | Tipe | Contoh | Strategi Cache |
|---------|------|--------|---------------|
| L1 | Tugas tetap | "pulang" | Langsung eksekusi |
| L2 | Tugas berparameter | "gali 10 berlian" | Cache dengan parameter |
| L3 | Tugas template | "bangun tempat berlindung" | Pencocokan template |
| L4 | Tugas dinamis | "bantu kalahkan Ender Dragon" | Reasoning AI |

### Contoh Skill YAML

```yaml
skill_id: mine_diamonds
name: "gali berlian"
level: L2
parameters:
  count: {type: int, default: 10, min: 1, max: 64}
steps:
  - action: pathfind
    target: {y: -59}
    note: "Menuju lapisan berlian"
  - action: dig_loop
    block: diamond_ore
    count: ${count}
  - action: pathfind
    target: home
    note: "Kembali ke basis"
```

---

## 🛡️ Sistem Keamanan

| Lapis | Mekanisme | Keterangan |
|-------|----------|-----------|
| L1 | Penilaian risiko | Setiap aksi dinilai 0-100 |
| L2 | Otorisasi operasi | Risiko tinggi perlu konfirmasi |
| L3 | Pengambilalihan darurat | Pemain bisa menginterupsi AI kapan saja |
| L4 | Log audit | Semua operasi dapat dilacak |
| L5 | Pembatasan zona aman | Membatasi jangkauan perusakan/penempatan |

---

## 🖥️ Panel Kontrol WebUI

Setelah mulai, akses `http://localhost:19951`, mendukung:

- 📊 Dashboard — Pemantauan status real-time
- 🛠️ Manajemen Skill — Edit YAML secara online
- 🧠 Sistem Memori — Lihat/hapus/backup
- 🤖 Konfigurasi Model — Ganti model AI secara hot-swap
- 💬 Panel Perintah — Instruksi bahasa alami
- 📋 Antrian Tugas — Lihat status eksekusi
- 📝 Pusat Log — Aliran log real-time

---

## ❓ FAQ

**Q: Apakah harus memasang Baritone?**
A: Tidak wajib. Baritone adalah dependensi opsional, tanpa Baritone otomatis fallback ke A* dasar pergerakan garis lurus.

**Q: Data memori disimpan di mana?**
A: Di direktori `data/memory/`, 5 file JSON, dipertahankan lintas sesi.

**Q: Bagaimana perlindungan bangunan diterapkan?**
A: Dua cara: ① Pendaftaran manual ② Deteksi otomatis (pindai setiap 60 detik).

**Q: Provider AI apa saja yang didukung?**
A: Format kompatibel OpenAI (termasuk DeepSeek/OpenRouter/MiMo, dll.) + format Anthropic.

**Q: Berapa besar image Docker?**
A: Sekitar 200MB, dibangun multi-stage berbasis python:3.11-slim.

---

## 🗺️ Peta Jalan

### v3.0 (Saat Ini) ✅
- [x] Sistem memori tiga lapis (ruang/jalur/strategi)
- [x] Navigasi cerdas (berbasis memori + integrasi Baritone)
- [x] Arsitektur Dual Agent (isolasi chat/operasi)
- [x] Perlindungan otomatis zona perlindungan bangunan
- [x] Miuix Console WebUI
- [x] Deployment sekali klik Windows/Linux
- [x] Image Docker + publikasi otomatis GHCR
- [x] GitHub Actions CI/CD

### v3.1 (Rencana)
- [ ] Input multimodal (analisis screenshot)
- [ ] Pasar Skill (impor/ekspor)
- [ ] Kolaborasi multi-pemain
- [ ] Interaksi suara

---

## 📄 Lisensi

MIT License. Lihat detail di [LICENSE](LICENSE).
