# 🧠 BlockMind

> **Fabric Mod + AI + hafıza sistemi** · Akıllı Minecraft oyun arkadaşı

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![MC](https://img.shields.io/badge/Minecraft-1.20~26.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT--NC-purple.svg)](LICENSE)

Fabric Mod hassas oyun arayüzü sağlar + Python AI kararlarını yönetir + hafıza sistemi oturumlar arası öğrenir. **Hem sunucu hem istemci modunu destekler**, tek kişilik oyun, LAN veya sunucularda kullanılabilir.

🌐 [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | **Türkçe**

---

## Neden BlockMind

### 1. Hafıza sistemi — AI öğrenir

Geleneksel AI oyun arkadaşları yeniden başlatmada her şeyi unutur. BlockMind'in üç katmanlı kalıcı hafızası vardır:

- **Mekansal hafıza**: Bina koruma alanlarını, tehlikeli bölgeleri, kaynak noktalarını otomatik hatırlar
- **Yol hafızası**: Başarılı yolları önbelleğe alır, başarısızları kara listeye ekler
- **Strateji hafızası**: Başarılı işlemler sıfır Token ile yeniden kullanılabilir stratejilere dönüşür

AI navigasyonda oyuncu binalarını otomatik olarak atlar, evi asla yıkmaz.

### 2. Çift Agent mimarisi — Token tasarrufu

```
Ana Agent (~50 Token/işlem): sadece sohbet + niyet tanıma
İşlem Agent (<1500 Token/işlem): durumsuz, kullan-at
```

Tek Agent (>4000 Token/işlem) ile karşılaştırıldığında %84 tasarruf.

### 3. Sunucu ve istemci modu

| Mod | Kurulum yeri | Oyuncu | Senaryo |
|-----|-------------|--------|---------|
| Sunucu | Sunucu `mods/` | FakePlayer (bot) | Sunucu 7×24 |
| İstemci | İstemci `mods/` | Yerel oyuncu | Tek kişilik / LAN |

### 4. Baritone + bina koruması

AI navigasyonda Baritone kullanır (kazma/köprü/yüzme) ancak bina koruma alanlarını otomatik olarak atlar. Hafızadaki binalar Baritone hariç tutma bölgeleri olarak enjekte edilir.

### 5. Skill DSL + pazar

YAML ile yeniden kullanılabilir AI becerileri tanımlama (kazma, tarım, inşaat), topluluk paylaşımı. AI'ın oluşturduğu beceriler otomatik kaydedilir ve sıfır Token ile çalıştırılır.

---

## Hızlı başlangıç

### Gereksinimler

- Python 3.10+ · Java 17+ · Minecraft 1.20.0 ~ 26.1.2

### Başlatma

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

### Yapılandırma

`config.yaml` dosyasını düzenleyin:

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

Başlatma sonrası `http://localhost:19951` adresine giderek kontrol paneline erişin.

---

## Mimari

```
┌──────────────── Minecraft ────────────────┐
│  BlockMind Fabric Mod (Java)              │
│  Durum toplama · İşlem yürütme            │
│  HTTP API :25580 · WebSocket              │
└──────────────────┬────────────────────────┘
                   │
┌──────────────────▼────────────────────────┐
│  BlockMind Python Backend                 │
│  ┌──────────┐  ┌──────────────────────┐  │
│  │ Ana      │  │ İşlem Agent          │  │
│  │ Agent    │  │ (durumsuz)           │  │
│  │ Sohbet   │  │ Skill eşleme/üretme  │  │
│  └─────┬────┘  └──────────┬───────────┘  │
│  ┌─────▼──────────────────▼───────────┐  │
│  │ Hafıza · Akıllı Navigasyon · Skill │  │
│  └────────────────┬───────────────────┘  │
│  ┌────────────────▼───────────────────┐  │
│  │ WebUI (MiuiX)                      │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## WebUI

`http://localhost:19951` — Lucide ikonları + MiuiX koyu tema

| Özellik | Açıklama |
|---------|----------|
| Gösterge paneli | Gerçek zamanlı durum, hızlı komutlar, olay akışı |
| Skill yönetimi | Çevrimiçi YAML düzenleme, tek tıkla çalıştırma |
| Skill pazarı | Topluluk becerileri, kurma, içe/dışa aktarma |
| Hafıza sistemi | Görüntüleme/yedekleme/temizleme/içe aktarma |
| Model ayarları | Çift Agent yapılandırması, sıcak geçiş |
| Güvenlik | Risk seviyesi, denetim günlüğü |
| Görev kuyruğu | İşlem durumu izleme |
| Günlük merkezi | WebSocket günlük akışı |

---

## API özeti

| Uç Nokta | Yöntem | Açıklama |
|----------|--------|----------|
| `/api/status` | GET | Oyuncu durumu |
| `/api/inventory` | GET | Envanter bilgisi |
| `/api/entities` | GET | Yakındaki varlıklar |
| `/api/move` | POST | Koordinata hareket |
| `/api/dig` | POST | Blok kazma |
| `/api/place` | POST | Blok koyma |
| `/api/attack` | POST | Varlığa saldırma |
| `/api/chat` | POST | Sohbet gönderme |

Tam belge: [Fabric Mod API](docs/MOD_BUILD.md)

---

## Desteklenen sürümler

| MC sürümü | Java | Durum |
|-----------|------|-------|
| 1.20.0 ~ 1.20.6 | 17~21 | ✅ |
| 1.21 ~ 1.21.4 | 21 | ✅ |
| 26.1 ~ 26.1.2 | 25 | ✅ En son |

---

## SSS

**S: Baritone yüklemek zorunda mıyım?** Hayır, olmadan temel A* kullanılır.

**S: Hafıza verileri nerede saklanıyor?** `data/memory/` klasöründe, 5 JSON dosyası.

**S: Hangi AI sağlayıcıları destekleniyor?** OpenAI uyumlu format (DeepSeek/OpenRouter/MiMo) + Anthropic.

**S: Tek kişilik oyunlarda kullanılabilir mi?** Evet, Mod'u istemci `mods/` klasörüne koyun.

---

## Lisans

MIT-NC — ticari kullanım yasaktır. Detaylar: [LICENSE](LICENSE).
