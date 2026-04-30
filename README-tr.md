# 🧠 BlockMind — Akıllı Minecraft AI Oyun Arkadaş Sistemi

> **Fabric Mod + AI Destekli + Hafıza Sistemi** · v3.0 · 2026-04-30

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![Fabric](https://img.shields.io/badge/Fabric-0.92+-yellow.svg)](https://fabricmc.net)
[![MC](https://img.shields.io/badge/Minecraft-1.20.x--1.21.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**Tek cümleyle özet:** Fabric Mod ile hassas oyun arayüzü + Python backend tarafından AI karar alma + hafıza sistemi ile oturumlar arası öğrenme sayesinde 7×24 saat otonom hayatta kalan Minecraft akıllı oyun arkadaşı.

🌐 [中文](README.md) | [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | [Español](README-es.md) | [Français](README-fr.md) | [Bahasa Indonesia](README-id.md) | [Italiano](README-it.md) | [Português](README-pt.md) | [Русский](README-ru.md) | [ภาษาไทย](README-th.md) | **Türkçe** | [Tiếng Việt](README-vi.md)
---

## 📖 İçindekiler

- [Proje Özellikleri](#-proje-özellikleri)
- [Sistem Mimarisi](#-sistem-mimarisi)
- [Hafıza Sistemi](#-hafıza-sistemi)
- [Akıllı Navigasyon](#-aklıllı-navigasyon)
- [Çift Agent Mimarisi](#-çift-agent-mimarisi)
- [Hızlı Başlangıç](#-hızlı-başlangıç)
- [Tek Tıkla Kurulum](#-tek-tıkla-kurulum)
- [Fabric Mod API](#-fabric-mod-api)
- [Skill DSL Sistemi](#-skill-dsl-sistemi)
- [Güvenlik Sistemi](#-güvenlik-sistemi)
- [WebUI Kontrol Paneli](#-webui-kontrol-paneli)
- [Dağıtım Kılavuzu](#-dağıtım-kılavuzu)
- [SSS](#-sss)
- [Yol Haritası](#-yol-haritası)

---

## ✨ Proje Özellikleri

### 🧠 Hafıza Sistemi — Oturumlar Arası Öğrenme (v3.0 Yeni)

```
Geleneksel yöntem:  Her yeniden başlatmada her şey unutulur, aynı hatalar tekrarlanır, Token israfı
Hafıza yöntemi:  Mekansal/yol/strateji üç katmanlı hafıza, kalıcı JSON, oturumlar arası yeniden kullanım
```

- **Mekansal Hafıza**: Bina koruma alanlarını, tehlikeli bölgeleri ve kaynak noktalarını otomatik algılar ve hatırlar
- **Yol Hafızası**: Başarılı yolları önbelleğe alır, başarısız yolları kara listeye alır, başarı oranı istatistikleri
- **Strateji Hafızası**: Başarılı işlemler otomatik olarak yeniden kullanılabilir stratejilere dönüşür, sıfır Token ile yeniden kullanım
- **Bina Koruması**: Navigasyon sırasında oyuncu binalarını otomatik olarak bypass eder, eviniz asla yıkılmaz

### 🛤️ Akıllı Navigasyon — Hafıza Destekli Yol Bulma (v3.0 Yeni)

```
Geleneksel yöntem:  walk_to(x,y,z) → Duvara çarpıp sıkışır / Binaları deler
Akıllı navigasyon:  Hafızaya bak → Önbellekten git → Baritone(koruma hariç) → A* geri dönüş
```

- **Önbellek Öncelikli**: Daha önce gidilen yollar doğrudan yeniden kullanılır, sıfır hesaplama
- **Baritone Entegrasyonu**: Topluluğun en güçlü yol bulma motoru, otomatik kazma/köprü/yüzme/lav kaçınma
- **Bina Koruma Alanı Enjeksiyonu**: Hafızadaki binalar otomatik olarak Baritone hariç tutma bölgelerine eklenir
- **Otomatik Öğrenme**: Her navigasyon sonucu otomatik olarak hafıza sistemine kaydedilir

### 🤖 Çift Agent Mimarisi — Sohbet ve İşlem İzolasyonu (v2.0 Yeni)

```
Ana Agent:  Sohbetten sorumlu, kalıcı bağlam, yalnızca niyet tanıma (~50 Token/işlem)
İşlem Agent:  Yürütmeden sorumlu, durumsuz taze bağlam (<1500 Token/işlem)
```

- **Ana Agent**: Sohbet bağlamını sürdürür, `[TASK:xxx]` etiketlerini tanır
- **İşlem Agent**: Durumsuz, kullan-at, bağlam patlamasını önler
- **Hafıza Enjeksiyonu**: AI karar verirken otomatik olarak hafıza bağlamı eklenir (bina koruma alanları, bilinen yollar vb.)

### 🔌 Fabric Mod Mimarisi — Hassas ve Güvenilir

- **Sıfır Protokol Çözümleme**: Doğrudan oyun içi API'ye erişim
- **13 HTTP Uç Noktası** + WebSocket gerçek zamanlı olaylar
- **Baritone İsteğe Bağlı Entegrasyon**: Varsa gelişmiş yol bulma, yoksa temel düz çizgi

### 🛡️ Beş Düzeyli Güvenlik Sistemi

| Düzey | Ad | Örnek | Strateji |
|------|------|------|------|
| 0 | Tamamen Güvenli | Hareket, zıplama | Otomatik yürütme |
| 1 | Düşük Risk | Toprak kazma, meşale koyma | Otomatik yürütme |
| 2 | Orta Risk | Cevher kazma, tarafsız yaratıklara saldırma | Otomatik yürütme |
| 3 | Yüksek Risk | TNT ateşleme, lava koyma | Oyuncu onayı gerekli |
| 4 | Ölümcül Risk | Komut bloğu koyma | Varsayılan olarak yasak |

---

## 🏗️ Sistem Mimarisi

```
┌──────────────────────────────────────────────────────────────┐
│                    Minecraft Sunucusu                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            BlockMind Fabric Mod (Java)                 │  │
│  │                                                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Durum      │ │Eylem     │ │Olay      │ │Baritone  │ │  │
│  │  │Toplayıcı  │ │Yürütücü  │ │Dinleyici │ │Yol bulma │ │  │
│  │  │Blok/varlık│ │Hareket/  │ │Sohbet/   │ │motoru    │ │  │
│  │  │/envanter/ │ │kazma/    │ │hasar/blok│ │(isteğe   │ │  │
│  │  │dünya      │ │koyma/    │ │değişikliği│ │bağlı)    │ │  │
│  │  │           │ │saldırı   │ │          │ │          │ │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │  │
│  │       └─────────────┼────────────┼────────────┘       │  │
│  │               HTTP API :25580 + WebSocket              │  │
│  └─────────────────────────────┼──────────────────────────┘  │
└────────────────────────────────┼─────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────┐
│                  BlockMind Python Backend                    │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                Çift Agent Mimarisi                     │  │
│  │  ┌─────────────────┐  ┌────────────────────────────┐  │  │
│  │  │ Ana Agent (sohbet│  │ İşlem Agent (yürütme,     │  │  │
│  │  │ kalıcı bağlam)   │  │ durumsuz)                  │  │  │
│  │  │ Niyet tanıma     │  │ Her seferinde taze bağlam  │  │  │
│  │  └────────┬────────┘  └─────────────┬──────────────┘  │  │
│  └───────────┼─────────────────────────┼─────────────────┘  │
│              │                         │                     │
│  ┌───────────▼─────────────────────────▼─────────────────┐  │
│  │               🧠 Hafıza Sistemi (GameMemory)          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Mekansal  │ │Yol       │ │Strateji  │ │Oyuncu    │ │  │
│  │  │Hafıza    │ │Hafızası  │ │Hafızası  │ │Hafızası  │ │  │
│  │  │Bina      │ │Başarılı  │ │Başarılı  │ │Ev konumu │ │  │
│  │  │koruma    │ │yollar    │ │stratejiler│ │Tercihler │ │  │
│  │  │alanları  │ │Başarısız │ │Başarısız │ │Etkileşim │ │  │
│  │  │Tehlikeli │ │kara liste│ │kayıtlar  │ │kayıtları │ │  │
│  │  │bölgeler  │ │Başarı    │ │Bağlam    │ │          │ │  │
│  │  │Kaynak    │ │oranı     │ │etiketleri│ │          │ │  │
│  │  │noktaları │ │istatistik│ │          │ │          │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │  │
│  │              Kalıcı JSON (data/memory/)                │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │ Enjeksiyon                    │
│  ┌──────────┐ ┌──────────────▼──────┐ ┌──────────────────┐  │
│  │ Skill    │ │ Akıllı Navigasyon   │ │ AI Karar Katmanı │  │
│  │Motoru    │ │ Hafıza→önbellek→    │ │ Hafıza bağlamı   │  │
│  │DSL çözüm │ │ Baritone→A* geri    │ │ enjeksiyonu       │  │
│  │eşleme    │ │ dönüş→otomatik      │ │ provider.py       │  │
│  │yürütme   │ │ öğrenme             │ │                   │  │
│  └──────────┘ └─────────────────────┘ └──────────────────┘  │
│  ┌──────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │ Güvenlik │ │ Sağlık       │ │ WebUI (Miuix Console)   │ │
│  │ Doğrulama│ │ İzleme       │ │ Karanlık tema/model     │ │
│  │Beş düzey │ │Üç düzey      │ │ yapılandırması          │ │
│  │risk kon- │ │kademeli      │ │                         │ │
│  │trolü     │ │düşürme       │ │                         │ │
│  └──────────┘ └──────────────┘ └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Veri Akışı Örneği

**Hafıza destekli akıllı navigasyon:**
```
Oyuncu "eve dön" dedi
  → Ana Agent görevi tanıdı [TASK:eve_dön]
  → İşlem Agent go_home Skill'ini eşleştirdi
  → SmartNavigator hafızaya sorguladı:
      ✅ Ev konumu: (65, 64, -120) oyuncu hafızasından
      ✅ Önbellek yolu: 3 kez gidildi, %100 başarı oranı
      ✅ Bina koruma alanı: Üssün 30 blok çevresinde yıkım yasak
      ✅ Tehlikeli bölge: (80,12,-50) lav var
  → Baritone navigasyonu:
      GoalBlock(65, 64, -120)
      + exclusion_zones=[üssün koruma alanı]
      → Otomatik olarak yoldan sapar, hiçbir binayı yıkım
  → Varış sonrası: yol önbelleği success_count+1
  → Sonraki eve dönüş: doğrudan önbellek yolunu kullanır, sıfır Token tüketimi
```

---

## 🧠 Hafıza Sistemi

### Üç Katmanlı Hafıza Mimarisi

| Katman | Saklanan İçerik | Kalıcı | Örnek |
|---|---------|--------|------|
| **Mekansal Hafıza** | Bina koruma alanları, tehlikeli bölgeler, kaynak noktaları, üs | ✅ JSON | "Üssün kapsamı: (50-100, 60-80, -150--90)" |
| **Yol Hafızası** | Başarılı yol önbelleği, başarısız yol kara listesi, başarı oranı | ✅ JSON | "Ev→maden ocağı: (70,64,-100) üzerinden, %100 başarı" |
| **Strateji Hafızası** | Başarılı strateji birikimi, başarısız dersler, bağlam etiketleri | ✅ JSON | "Madencilikte önce meşale koyup sonra kaz, en verimli" |
| **Oyuncu Hafızası** | Ev konumu, tercih edilen araçlar, etkileşim kayıtları | ✅ JSON | "Steve'in evi (100,64,200) konumunda" |
| **Dünya Hafızası** | Doğma noktası, güvenli noktalar, önemli olaylar | ✅ JSON | "Doğma noktası (0,64,0), güvenli nokta listesi" |

### Otomatik Bina Koruması

```python
# Bina koruma alanı kaydet (AI yıkımı yasak)
memory.register_building("Ana şehir", center=(100, 64, 200), radius=30)
# → Navigasyon sırasında otomatik olarak Baritone exclusion_zones'a eklenir
# → type: "no_break" + "no_place"
# → AI koruma alanında blok yıkamaz/koyamaz

# Otomatik algılama (her 60 saniyede çevreyi tarar)
navigator.auto_detect_and_memorize()
# → Ardışık yapı blokları algılanırsa → otomatik olarak koruma alanı olarak kaydedilir
# → Lav/ateş algılanırsa → otomatik olarak tehlikeli bölge olarak kaydedilir
# → Cevher yığını algılanırsa → otomatik olarak kaynak noktası olarak kaydedilir
```

### Yol Önbellek Mekanizması

```python
# İlk navigasyon: AI planlama + yürütme
result = await navigator.goto(100, 64, 200)
# → Yol önbelleğe alındı: success_count=1, success_rate=100%

# İkinci navigasyon: doğrudan önbellekten
result = await navigator.goto(100, 64, 200)
# → Önbellek yolu bulundu, doğrudan yürütülür, sıfır hesaplama

# Başarısız yol: otomatik öğrenme
# → fail_count >= 3 → otomatik olarak kara listeye alınır
# → Sonraki sefere yeniden planlanır, eski yoldan gidilmez
```

### Strateji Otomatik Birikimi

```python
# İşlem Agent başarılı olduktan sonra otomatik olarak kaydeder
memory.record_strategy(
    task_type="mine",
    description="Önce meşale koyup sonra madencilik yap",
    action_sequence=[...],
    success=True,
    context_tags=["nighttime", "cave"],
)

# Aynı görev türünde otomatik olarak en iyi strateji eşleştirilir
best = memory.get_best_strategy("mine", context_tags=["nighttime"])
# → En yüksek başarı oranına sahip stratejiyi döndürür
```

### AI Hafıza Bağlamı Enjeksiyonu

```python
# Her AI kararında otomatik olarak hafıza enjekte edilir
memory_context = memory.get_ai_context()
# Çıktı:
# [Hafıza Sistemi]
# Üs:
#   - Ev: (50, 64, -100) (yarıçap 30)
# Bina koruma alanları (yıkım yasak):
#   - Ana şehir: (100, 64, 200) (yarıçap 20)
# Tehlikeli bölgeler:
#   - Lav gölü: (80, 12, -50) (lav)
# Bilinen güvenilir yollar: 3 adet
# Doğrulanmış stratejiler: 5 adet
```

---

## 🛤️ Akıllı Navigasyon

### Navigasyon Akışı

```
SmartNavigator.goto(x, y, z)
  │
  ├── 1. Güvenlik kontrolü
  │     └── Hedef koruma alanında mı? → Uyar ama reddetme
  │
  ├── 2. Önbellek yol sorgusu
  │     └── Güvenilir önbellek var mı? → Doğrudan önbellek yolunu yürüt
  │
  ├── 3. Navigasyon bağlamını al
  │     ├── Hariç tutulan bölgeler (bina koruma alanları)
  │     ├── Tehlikeli bölgeler (lav, uçurum)
  │     └── Güvenilir yol referansları
  │
  ├── 4. Baritone yol bulma (tercih edilen)
  │     ├── exclusion_zones enjeksiyonu
  │     ├── Otomatik kazma / köprü kurma / yüzme
  │     └── Düşme maliyeti / lav kaçınma
  │
  ├── 5. A* yol bulma (geri dönüş)
  │     └── Temel ızgara A* + blok geçilebilirlik kontrolü
  │
  └── 6. Sonucu kaydet
        ├── Başarılı → cache_path(success=True)
        └── Başarısız → cache_path(success=False) + muhtemelen kara liste
```

### Baritone Entegrasyonu

| Özellik | Baritone | Temel A* |
|------|----------|---------|
| Yol bulma algoritması | Geliştirilmiş A* + maliyet sezgisi | Standart A* |
| Kazma yolu | ✅ Otomatik engelleri kazarak geçer | ❌ |
| Köprü kurma | ✅ scaffold modu | ❌ |
| Yüzme | ✅ | ❌ |
| Dikey hareket | ✅ Zıplama/merdiven/sarmaşık | ⚠️ Yalnızca 1 blok |
| Lav kaçınma | ✅ Maliyet cezası | ❌ |
| Düşme maliyeti | ✅ Sezgi fonksiyonuna dahil | ❌ |
| Hariç tutulan bölgeler | ✅ `exclusionAreas` | ❌ |
| **Bina koruması** | ✅ `no_break` bölgeleri enjekte eder | ❌ |

### Hariç Tutulan Bölge Türleri

| Tür | Açıklama | Kaynak |
|------|------|------|
| `no_break` | Blok yıkımı yasak | Bina koruma alanları, üs |
| `no_place` | Blok koyma yasak | Bina koruma alanları |
| `avoid` | Tamamen kaçınılır | Tehlikeli bölgeler (lav vb.) |

---

## 🤖 Çift Agent Mimarisi

### Neden Çift Agent Gerekli?

```
Tek Agent sorunu:
  Sohbet bağlamı + işlem bağlamı → Token patlaması (>4000/işlem)
  İşlem hatası sohbeti kirletir → Sohbet deneyimi kötüleşir
  Her işlemde tam sohbet geçmişi taşınır → İsraf

Çift Agent çözümü:
  Ana Agent: Yalnızca sohbet, kayan pencere 20 mesaj, ~50 Token/işlem
  İşlem Agent: Durumsuz, taze bağlam, <1500 Token/işlem
```

### Akış

```
Oyuncu mesajı
  → Ana Agent sohbet (kalıcı bağlam)
  → [TASK:xxx] etiketi tanımlandı
  → Görev açıklaması çıkarıldı
  → İşlem Agent yürütür (durumsuz):
      ├── Skill eşleme sorgusu
      ├── Hafıza bağlamı enjeksiyonu
      ├── L1/L2: Önbelleklenmiş Skill yürütülür
      ├── L3: AI şablonu doldurur + yürütür
      └── L4: AI tam çıkarım + yürütür
  → Ana Agent yanıtı biçimlendirir → Oyuncuya
```

---
## 🚀 Hızlı Başlangıç

### Ortam Gereksinimleri

| Bileşen | Gereksinim |
|------|------|
| Python | 3.10+ |
| Java | 17+ |
| Minecraft | 1.19.4 - 1.21.4 |
| Fabric Loader | 0.15+ |

---

## 📦 Tek Tıkla Kurulum

### İndirme

[GitHub Releases](https://github.com/bmbxwbh/BlockMind/releases/latest) adresinden indirin:

| Dosya | Açıklama |
|------|------|
| `blockmind-mod-1.0.0.jar` | Fabric Mod (sunucu mods/ klasörüne koyun) |
| `Source code` (zip/tar) | Tam kaynak kodu |

### Linux / macOS Tek Tıkla Başlatma

```bash
# Klonla
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

# Tek tıkla başlat (otomatik bağımlılık kurulumu + MC sunucu + BlockMind + WebUI)
chmod +x start.sh
./start.sh
```

> `start.sh` otomatik olarak: Python/Java algılama → bağımlılık kurulumu → mevcut MC sunucu tarama → sürüm seçme ve kurma → tümünü başlatma

### Windows Tek Tıkla Başlatma

```cmd
:: Klonla (veya zip indirip çıkarın)
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

:: Tek tıkla kurulum
install.bat

:: Tek tıkla başlat (MC sunucu + BlockMind + WebUI)
start_all.bat
```

> Detaylı adımlar için [Windows Dağıtım Kılavuzu](docs/WINDOWS.md) belgesine bakın

### Docker Dağıtımı

```bash
# İmajı çek
docker pull ghcr.io/bmbxwbh/blockmind:latest

# Yapılandırma şablonunu indir
wget https://raw.githubusercontent.com/bmbxwbh/BlockMind/main/config.example.yaml -O config.yaml
# config.yaml dosyasını düzenleyerek AI model yapılandırmanızı girin

# Başlat
docker run -d \
  --name blockmind \
  -p 19951:19951 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v blockmind-data:/data \
  ghcr.io/bmbxwbh/blockmind:latest
```

veya docker-compose kullanın:

```bash
git clone https://github.com/bmbxwbh/BlockMind.git && cd BlockMind
cp config.example.yaml config.yaml
# config.yaml dosyasını düzenleyin
docker compose up -d
```

```bash
# Günlükleri görüntüle
docker compose logs -f blockmind
# Durdur
docker compose down
```

### Yapılandırma

`config.yaml` dosyasını düzenleyin:

```yaml
ai:
  main_agent:
    provider: "openai"          # openai veya anthropic
    api_key: "sk-your-key"
    model: "gpt-4o"             # Model adınız
    base_url: ""                # Özel API adresi (isteğe bağlı)

webui:
  enabled: true
  port: 19951
  auth:
    password: "your-password"   # WebUI giriş şifresi
```

Başlatma sonrası `http://localhost:19951` adresine giderek kontrol paneline erişin.

---

## 🔌 Fabric Mod API

### Durum Sorgulama

| Uç Nokta | Yöntem | Açıklama |
|------|------|------|
| `/health` | GET | Sağlık kontrolü |
| `/api/status` | GET | Oyuncu durumu |
| `/api/world` | GET | Dünya durumu |
| `/api/inventory` | GET | Envanter bilgisi |
| `/api/entities?radius=32` | GET | Yakındaki varlıklar |
| `/api/blocks?radius=16` | GET | Yakındaki bloklar |

### Eylem Yürütme

| Uç Nokta | Yöntem | Açıklama |
|------|------|------|
| `/api/move` | POST | Koordinata hareket et |
| `/api/dig` | POST | Blok kaz |
| `/api/place` | POST | Blok koy |
| `/api/attack` | POST | Varlığa saldır |
| `/api/eat` | POST | Ye |
| `/api/look` | POST | Koordinata bak |
| `/api/chat` | POST | Sohbet gönder |

### Yol Planlama

| Uç Nokta | Yöntem | Açıklama |
|------|------|------|
| `/api/pathfind` | POST | Yol navigasyonu (Baritone/A*) |
| `/api/pathfind/stop` | POST | Navigasyonu durdur |
| `/api/pathfind/status` | GET | Navigasyon durumu |

### Olay Bildirimleri

Mod, WebSocket üzerinden olaylar gönderir:
- `player_damaged` — Oyuncu hasar aldı
- `entity_attack` — Saldırıya uğradı
- `health_low` — Can düşük
- `inventory_full` — Envanter dolu
- `block_broken` — Blok kazma tamamlandı

---

## 📝 Skill DSL Sistemi

### Görev Sınıflandırması

| Düzey | Tür | Örnek | Önbellek stratejisi |
|------|------|------|----------|
| L1 | Sabit görev | "Eve dön" | Doğrudan yürütme |
| L2 | Parametreli görev | "10 elmas kaz" | Parametreli önbellek |
| L3 | Şablon görev | "Barınak inşa et" | Şablon eşleme |
| L4 | Dinamik görev | "Ender Dragon'u yenmeme yardım et" | AI çıkarımı |

### Skill YAML Örneği

```yaml
skill_id: mine_diamonds
name: "Elmas kaz"
level: L2
parameters:
  count: {type: int, default: 10, min: 1, max: 64}
steps:
  - action: pathfind
    target: {y: -59}
    note: "Elmas katmanına git"
  - action: dig_loop
    block: diamond_ore
    count: ${count}
  - action: pathfind
    target: home
    note: "Üsse dön"
```

---

## 🛡️ Güvenlik Sistemi

| Katman | Mekanizma | Açıklama |
|------|------|------|
| L1 | Risk değerlendirmesi | Her eylem 0-100 arası puanlanır |
| L2 | İşlem onayı | Yüksek risk için onay gerekli |
| L3 | Acil müdahale | Oyuncu istediği zaman AI'yi durdurabilir |
| L4 | Denetim günlüğü | Tüm işlemler izlenebilir |
| L5 | Güvenli bölge kısıtlaması | Yıkım/koyma alanı kısıtlaması |

---

## 🖥️ WebUI Kontrol Paneli

Başlatma sonrası `http://localhost:19951` adresine gidin, desteklenen özellikler:

- 📊 Gösterge paneli — Gerçek zamanlı durum izleme
- 🛠️ Skill yönetimi — Çevrimiçi YAML düzenleme
- 🧠 Hafıza sistemi — Görüntüleme/temizleme/yedekleme
- 🤖 Model yapılandırması — Sıcak geçişli AI modeli
- 💬 Komut paneli — Doğal dil komutları
- 📋 Görev kuyruğu — Yürütme durumunu görüntüleme
- 📝 Günlük merkezi — Gerçek zamanlı günlük akışı

---

## ❓ SSS

**S: Baritone yüklemek zorunda mıyım?**
C: Hayır. Baritone isteğe bağlı bir bağımlılıktır, yoksa otomatik olarak temel A* düz çizgi hareketine geri döner.

**S: Hafıza verileri nerede saklanıyor?**
C: `data/memory/` dizininde, 5 JSON dosyası, oturumlar arası korunur.

**S: Bina koruması nasıl devreye giriyor?**
C: İki şekilde: ① Manuel kayıt ② Otomatik algılama (her 60 saniyede tarama).

**S: Hangi AI sağlayıcılarını destekliyor?**
C: OpenAI uyumlu format (DeepSeek/OpenRouter/MiMo dahil) + Anthropic formatı.

**S: Docker imajı ne kadar büyük?**
C: Yaklaşık 200MB, python:3.11-slim tabanlı çok aşamalı yapı.

---

## 🗺️ Yol Haritası

### v3.0 (Mevcut) ✅
- [x] Üç katmanlı hafıza sistemi (mekansal/yol/strateji)
- [x] Akıllı navigasyon (hafıza destekli + Baritone entegrasyonu)
- [x] Çift Agent mimarisi (sohbet/işlem izolasyonu)
- [x] Otomatik bina koruma alanı koruması
- [x] Miuix Console WebUI
- [x] Windows/Linux tek tıkla kurulum
- [x] Docker imajı + GHCR otomatik yayınlama
- [x] GitHub Actions CI/CD

### v3.1 (Planlanan)
- [ ] Çoklu girdi (ekran görüntüsü analizi)
- [ ] Skill pazarı (içe/dışa aktarma)
- [ ] Çok oyunculu işbirliği
- [ ] Sesli etkileşim

---

## 📄 Lisans

MIT License. Ayrıntılar için [LICENSE](LICENSE) dosyasına bakın.
