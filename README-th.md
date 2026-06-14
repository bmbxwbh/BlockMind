# 🧠 BlockMind

> **Fabric Mod + AI + ระบบความทรงจำ** · คู่หูอัจฉริยะ Minecraft

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![MC](https://img.shields.io/badge/Minecraft-1.20~26.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT--NC-purple.svg)](LICENSE)

Fabric Mod ให้ API เกมที่แม่นยำ + Python ขับเคลื่อนการตัดสินใจ AI + ระบบความทรงจำเรียนรู้ข้ามเซสชัน **รองรับทั้งโหมดเซิร์ฟเวอร์และไคลเอนต์** ใช้ได้ทั้งเกมคนเดียว LAN หรือเซิร์ฟเวอร์

🌐 [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | [Español](README-es.md) | **ภาษาไทย**

---

## ทำไมต้อง BlockMind

### 1. ระบบความทรงจำ — AI เรียนรู้

AI คู่หูแบบเดิมลืมทุกอย่างทุกครั้งที่รีสตาร์ท BlockMind มีความทรงจำ 3 ชั้นถาวร:

- **ความทรงจำเชิงพื้นที่**: จดจำเขตอาคารป้องกัน พื้นที่อันตราย จุดทรัพยากรโดยอัตโนมัติ
- **ความทรงจำเชิงเส้นทาง**: จำเส้นทางสำเร็จ แบล็คลิสต์เส้นทางล้มเหลว
- **ความทรงจำเชิงกลยุทธ์**: ปฏิบัติการสำเร็จกลายเป็นกลยุทธ์ใช้ซ้ำได้ Zero Token

AI หลบหลีกอาคารผู้เล่นโดยอัตโนมัติขณะนำทาง ไม่ทำลายบ้าน

### 2. สถาปัตยกรรม Dual Agent — ประหยัด Token

```
Agent หลัก (~50 Token/ครั้ง): เฉพาะแชท + ระบุเจตนา
Agent ปฏิบัติการ (<1500 Token/ครั้ง): ไม่มี state ใช้แล้วทิ้ง
```

เปรียบเทียบกับ Single Agent (>4000 Token/ครั้ง) ประหยัด 84%

### 3. โหมดเซิร์ฟเวอร์และไคลเอนต์

| โหมด | ตำแหน่งติดตั้ง | ผู้เล่น | สถานการณ์ |
|------|----------------|---------|-----------|
| เซิร์ฟเวอร์ | `mods/` บนเซิร์ฟเวอร์ | FakePlayer (บอท) | เซิร์ฟเวอร์ 7×24 |
| ไคลเอนต์ | `mods/` บนไคลเอนต์ | ผู้เล่นท้องถิ่น | เกมคนเดียว / LAN |

### 4. Baritone + ป้องกันอาคาร

AI ใช้ Baritone นำทาง (ขุดทาง/สร้างสะพาน/ว่ายน้ำ) แต่หลบเขตอาคารป้องกันโดยอัตโนมัติ อาคารในความทรงจำถูกฉีดเป็น exclusion zones ของ Baritone

### 5. Skill DSL + ตลาด

กำหนด Skill AI ใช้ซ้ำได้ด้วย YAML (ขุดแร่ ทำฟาร์ม สร้างบ้าน) แชร์ในชุมชน Skill ที่ AI สร้างจะถูกบันทึกและทำงานครั้งถัดไป Zero Token

---

## เริ่มต้นอย่างรวดเร็ว

### ความต้องการ

- Python 3.10+ · Java 17+ · Minecraft 1.20.0 ~ 26.1.2

### เริ่มต้น

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

### การตั้งค่า

แก้ไข `config.yaml`:

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

หลังเริ่มต้น เปิด `http://localhost:19951` เพื่อเข้าแผงควบคุม

---

## สถาปัตยกรรม

```
┌──────────────── Minecraft ────────────────┐
│  BlockMind Fabric Mod (Java)              │
│  เก็บสถานะ · ดำเนินการ · ฟังเหตุการณ์  │
│  HTTP API :25580 · WebSocket              │
└──────────────────┬────────────────────────┘
                   │
┌──────────────────▼────────────────────────┐
│  BlockMind Python Backend                 │
│  ┌──────────┐  ┌──────────────────────┐  │
│  │ Agent    │  │ Agent ปฏิบัติการ     │  │
│  │ หลัก     │  │ (ไม่มี state)        │  │
│  │ แชท      │  │ จับคู่/สร้าง Skill   │  │
│  └─────┬────┘  └──────────┬───────────┘  │
│  ┌─────▼──────────────────▼───────────┐  │
│  │ ระบบความทรงจำ · นำทาง · Skill    │  │
│  └────────────────┬───────────────────┘  │
│  ┌────────────────▼───────────────────┐  │
│  │ WebUI (MiuiX)                      │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## WebUI

`http://localhost:19951` — ไอคอน Lucide + ธีมมืด MiuiX

| ฟีเจอร์ | คำอธิบาย |
|---------|----------|
| แดชบอร์ด | สถานะเรียลไทม์ คำสั่งด่วน สตรีมเหตุการณ์ |
| จัดการ Skill | แก้ไข YAML ออนไลน์ คลิกเดียวทำงาน |
| ตลาด Skill | ทักษะชุมชน ติดตั้ง นำเข้า/ส่งออก |
| ระบบความทรงจำ | ดู/สำรอง/ล้าง/นำเข้า/ส่งออก |
| ตั้งค่าโมเดล | ตั้งค่า Dual Agent สลับร้อน |
| ตั้งค่าความปลอดภัย | ระดับความเสี่ยง บันทึกตรวจสอบ |
| คิวงาน | ติดตามสถานะการทำงาน |
| ศูนย์บันทึก | สตรีมบันทึก WebSocket เรียลไทม์ |

---

## สรุป API

| Endpoint | เมธอด | คำอธิบาย |
|----------|--------|----------|
| `/api/status` | GET | สถานะผู้เล่น |
| `/api/inventory` | GET | ข้อมูลกระเป๋า |
| `/api/entities` | GET | เอนทิตีใกล้เคียง |
| `/api/move` | POST | เดินไปพิกัด |
| `/api/dig` | POST | ขุดบล็อก |
| `/api/place` | POST | วางบล็อก |
| `/api/attack` | POST | โจมตีเอนทิตี |
| `/api/chat` | POST | ส่งข้อความแชท |

เอกสารฉบับเต็มที่ [Fabric Mod API](docs/MOD_BUILD.md)

---

## เวอร์ชันที่รองรับ

| MC เวอร์ชัน | Java | สถานะ |
|--------------|------|-------|
| 1.20.0 ~ 1.20.6 | 17~21 | ✅ |
| 1.21 ~ 1.21.4 | 21 | ✅ |
| 26.1 ~ 26.1.2 | 25 | ✅ ล่าสุด |

---

## FAQ

**Q: ต้องติดตั้ง Baritone ไหม?** ไม่จำเป็น ไม่มีก็ใช้ A* พื้นฐาน

**Q: ข้อมูลความทรงจำเก็บที่ไหน?** ใน `data/memory/` มี 5 ไฟล์ JSON

**Q: รองรับ AI provider ใดบ้าง?** รูปแบบ OpenAI (DeepSeek/OpenRouter/MiMo) + Anthropic

**Q: เล่นเกมคนเดียวได้ไหม?** ได้ ใส่ Mod ใน `mods/` ของไคลเอนต์

---

## ใบอนุญาต

MIT-NC — ห้ามใช้เชิงพาณิชย์ รายละเอียดที่ [LICENSE](LICENSE)
