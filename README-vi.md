# 🧠 BlockMind

> **Fabric Mod + AI + hệ thống ghi nhớ** · Bạn đồng hành thông minh Minecraft

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![MC](https://img.shields.io/badge/Minecraft-1.20~26.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT--NC-purple.svg)](LICENSE)

Fabric Mod cung cấp API game chính xác + Python điều khiển quyết định AI + hệ thống ghi nhớ học liên phiên. **Hỗ trợ cả chế độ server và client**, dùng được trong game đơn, LAN hoặc server.

🌐 [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | **Tiếng Việt**

---

## Tại sao chọn BlockMind

### 1. Hệ thống ghi nhớ — AI học hỏi

Bạn đồng hành AI truyền thống quên hết khi khởi động lại. BlockMind có 3 lớp ghi nhớ vĩnh viễn:

- **Ghi nhớ không gian**: Tự động nhớ vùng bảo vệ công trình, vùng nguy hiểm, điểm tài nguyên
- **Ghi nhớ đường dẫn**: Cache đường thành công, blacklist đường thất bại
- **Ghi nhớ chiến lược**: Tác vụ thành công biến thành chiến lược tái sử dụng Zero Token

AI tự động tránh công trình người chơi khi điều hướng, không bao giờ phá nhà.

### 2. Kiến trúc Dual Agent — Tiết kiệm Token

```
Agent Chính (~50 Token/lần): chỉ chat + nhận diện ý định
Agent Thao tác (<1500 Token/lần): không trạng thái, dùng xong bỏ
```

So với Single Agent (>4000 Token/lần), tiết kiệm 84%.

### 3. Chế độ Server và Client

| Chế Độ | Vị trí cài | Người chơi | Tình huống |
|--------|-----------|------------|-----------|
| Server | `mods/` trên server | FakePlayer (bot) | Server 7×24 |
| Client | `mods/` trên client | Người chơi local | Game đơn / LAN |

### 4. Baritone + bảo vệ công trình

AI dùng Baritone điều hướng (đào đường/xây cầu/bơi), nhưng tự động tránh vùng bảo vệ công trình. Công trình trong ghi nhớ được tiêm vào Baritone exclusion zones.

### 5. Skill DSL + thị trường

Định nghĩa kỹ năng AI tái sử dụng bằng YAML (đào mỏ, nông trại, xây nhà), chia sẻ cộng đồng. Skill AI tạo ra tự động lưu và thực thi lần sau Zero Token.

---

## Bắt đầu nhanh

### Yêu cầu

- Python 3.10+ · Java 17+ · Minecraft 1.20.0 ~ 26.1.2

### Khởi động

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

### Cấu hình

Chỉnh sửa `config.yaml`:

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

Sau khi khởi động truy cập `http://localhost:19951` để vào bảng điều khiển.

---

## Kiến trúc

```
┌──────────────── Minecraft ────────────────┐
│  BlockMind Fabric Mod (Java)              │
│  Thu thập trạng thái · Thực hiện hành động│
│  HTTP API :25580 · WebSocket              │
└──────────────────┬────────────────────────┘
                   │
┌──────────────────▼────────────────────────┐
│  BlockMind Python Backend                 │
│  ┌──────────┐  ┌──────────────────────┐  │
│  │ Agent    │  │ Agent Thao tác       │  │
│  │ Chính    │  │ (không trạng thái)   │  │
│  │ Chat     │  │ Ghép/Tạo Skill       │  │
│  └─────┬────┘  └──────────┬───────────┘  │
│  ┌─────▼──────────────────▼───────────┐  │
│  │ Ghi nhớ · Điều hướng · Skill       │  │
│  └────────────────┬───────────────────┘  │
│  ┌────────────────▼───────────────────┐  │
│  │ WebUI (MiuiX)                      │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## WebUI

`http://localhost:19951` — Lucide icons + MiuiX dark theme

| Tính năng | Mô tả |
|-----------|-------|
| Dashboard | Trạng thái realtime, lệnh nhanh, stream sự kiện |
| Quản lý Skill | Chỉnh sửa YAML online, thực thi một click |
| Thị trường Skill | Skill cộng đồng, cài đặt, nhập/xuất |
| Hệ thống ghi nhớ | Xem/sao lưu/dọn dẹp/nhập/xuất |
| Cấu hình Model | Cấu hình Dual Agent, chuyển đổi nóng |
| Cài đặt Bảo mật | Mức rủi ro, log kiểm toán |
| Hàng đợi Task | Theo dõi trạng thái thực thi |
| Trung tâm Log | Stream log WebSocket realtime |

---

## Tóm tắt API

| Endpoint | Phương thức | Mô tả |
|----------|-------------|-------|
| `/api/status` | GET | Trạng thái người chơi |
| `/api/inventory` | GET | Thông tin túi đồ |
| `/api/entities` | GET | Thực thể lân cận |
| `/api/move` | POST | Di chuyển đến tọa độ |
| `/api/dig` | POST | Đào khối |
| `/api/place` | POST | Đặt khối |
| `/api/attack` | POST | Tấn công thực thể |
| `/api/chat` | POST | Gửi tin nhắn chat |

Tài liệu đầy đủ: [Fabric Mod API](docs/MOD_BUILD.md)

---

## Phiên bản hỗ trợ

| MC phiên bản | Java | Trạng thái |
|--------------|------|------------|
| 1.20.0 ~ 1.20.6 | 17~21 | ✅ |
| 1.21 ~ 1.21.4 | 21 | ✅ |
| 26.1 ~ 26.1.2 | 25 | ✅ Mới nhất |

---

## FAQ

**Q: Có phải cài Baritone không?** Không bắt buộc, không có thì dùng A* cơ bản.

**Q: Dữ liệu ghi nhớ lưu ở đâu?** Trong `data/memory/`, 5 file JSON.

**Q: Hỗ trợ AI provider nào?** Định dạng OpenAI (DeepSeek/OpenRouter/MiMo) + Anthropic.

**Q: Dùng được trong game đơn không?** Được, đặt Mod vào `mods/` của client.

---

## Giấy phép

MIT-NC — cấm sử dụng thương mại. Chi tiết: [LICENSE](LICENSE).
