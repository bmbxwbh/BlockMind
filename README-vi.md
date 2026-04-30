# 🧠 BlockMind — Hệ thống Bạn đồng hành AI Minecraft Thông minh

> **Fabric Mod + AI Động lực + Hệ thống Ghi nhớ** · v3.0 · 2026-04-30

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org)
[![Fabric](https://img.shields.io/badge/Fabric-0.92+-yellow.svg)](https://fabricmc.net)
[![MC](https://img.shields.io/badge/Minecraft-1.20.x--1.21.x-green.svg)](https://minecraft.net)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**Tóm tắt một câu:** Fabric Mod cung cấp giao diện game chính xác + Backend Python điều khiển quyết định AI + Hệ thống ghi nhớ học liên phiên, tạo ra bạn đồng hành Minecraft AI sống sót tự chủ 7×24 giờ.

🌐 [中文](README.md) | [English](README-en.md) | [日本語](README-ja.md) | [한국어](README-ko.md) | [العربية](README-ar.md) | [Deutsch](README-de.md) | [Español](README-es.md) | [Français](README-fr.md) | [Bahasa Indonesia](README-id.md) | [Italiano](README-it.md) | [Português](README-pt.md) | [Русский](README-ru.md) | [ภาษาไทย](README-th.md) | [Türkçe](README-tr.md) | **Tiếng Việt**
---

## 📖 Mục lục

- [Đặc điểm Dự án](#-đặc-điểm-dự-án)
- [Kiến trúc Hệ thống](#-kiến-trúc-hệ-thống)
- [Hệ thống Ghi nhớ](#-hệ-thống-ghi-nhớ)
- [Điều hướng Thông minh](#-điều-hướng-thông-minh)
- [Kiến trúc Đôi Agent](#-kiến-trúc-đôi-agent)
- [Bắt đầu Nhanh](#-bắt-đầu-nhanh)
- [Triển khai Một chạm](#-triển-khai-một-chạm)
- [Fabric Mod API](#-fabric-mod-api)
- [Hệ thống Skill DSL](#-hệ-thống-skill-dsl)
- [Hệ thống Bảo mật](#-hệ-thống-bảo-mật)
- [Bảng điều khiển WebUI](#-bảng-điều-khiển-webui)
- [Hướng dẫn Triển khai](#-hướng-dẫn-triển-khai)
- [Câu hỏi Thường gặp](#-câu-hỏi-thường-gặp)
- [Lộ trình](#-lộ-trình)

---

## ✨ Đặc điểm Dự án

### 🧠 Hệ thống Ghi nhớ — Học liên phiên (mới trong v3.0)

```
Cách truyền thống:  Mỗi lần khởi động lại quên hết, lặp lại lỗi, lặp lại tiêu tốn Token
Cách ghi nhớ:  Không gian/Đường dẫn/Chiến lược — ba lớp ghi nhớ, JSON vĩnh viễn, tái sử dụng liên phiên
```

- **Ghi nhớ Không gian**: Tự động phát hiện và ghi nhớ vùng bảo vệ công trình, vùng nguy hiểm, điểm tài nguyên
- **Ghi nhớ Đường dẫn**: Cache đường đi thành công, blacklist đường đi thất bại, thống kê tỷ lệ thành công
- **Ghi nhớ Chiến lược**: Tác vụ thành công tự động chuyển thành chiến lược tái sử dụng, zero Token khi dùng lại
- **Bảo vệ Công trình**: Điều hướng tự động tránh nhà người chơi, không lo phá nhà

### 🛤️ Điều hướng Thông minh — Tìm đường dựa trên Ghi nhớ (mới trong v3.0)

```
Cách truyền thống:  walk_to(x,y,z) → kẹt tường / phá xuyên công trình
Điều hướng thông minh:  Truy vấn ghi nhớ → đi cache → Baritone(loại trừ vùng bảo vệ) → A* dự phòng
```

- **Ưu tiên Cache**: Đường đã đi được tái sử dụng trực tiếp, không tính toán
- **Tích hợp Baritone**: Công cụ tìm đường mạnh nhất cộng đồng, tự động đào đường/xây cầu/bơi/tránh dung nham
- **Tiêm vùng bảo vệ Công trình**: Nhà trong ghi nhớ tự động tiêm vào vùng loại trừ Baritone
- **Tự động học**: Mỗi kết quả điều hướng tự động ghi vào hệ thống ghi nhớ

### 🤖 Kiến trúc Đôi Agent — Cô lập Trò chuyện và Thao tác (mới trong v2.0)

```
Agent Chính:  Phụ trách trò chuyện, ngữ cảnh bền vững, chỉ nhận diện ý định (~50 Token/lần)
Agent Thao tác: Phụ trách thực thi, không trạng thái, ngữ cảnh mới mỗi lần (<1500 Token/lần)
```

- **Agent Chính**: Giữ ngữ cảnh trò chuyện, nhận diện thẻ `[TASK:xxx]`
- **Agent Thao tác**: Không trạng thái, dùng xong bỏ, tránh ngữ cảnh quá tải
- **Tiêm Ghi nhớ**: Khi AI ra quyết định tự động tiêm ngữ cảnh ghi nhớ (vùng bảo vệ nhà, đường đã biết, v.v.)

### 🔌 Kiến trúc Fabric Mod — Chính xác và Đáng tin cậy

- **Không phân tích giao thức**: Gọi trực tiếp API nội bộ game
- **13 HTTP Endpoint** + WebSocket sự kiện thời gian thực
- **Tùy chọn tích hợp Baritone**: Có thì tìm đường nâng cao, không thì đường thẳng cơ bản

### 🛡️ Hệ thống Bảo mật Năm cấp

| Cấp | Tên | Ví dụ | Chiến lược |
|-----|-----|-------|-----------|
| 0 | Hoàn toàn An toàn | Di chuyển, nhảy | Tự động thực thi |
| 1 | Rủi ro Thấp | Đào đất, đặt meo | Tự động thực thi |
| 2 | Rủi ro Trung bình | Đánh quặng, tấn công sinh vật trung lập | Tự động thực thi |
| 3 | Rủi ro Cao | Đốt TNT, đổ dung nham | Cần người chơi xác nhận |
| 4 | Rủi ro Chết người | Đặt khối lệnh | Mặc định cấm |

---

## 🏗️ Kiến trúc Hệ thống

```
┌──────────────────────────────────────────────────────────────┐
│                    Minecraft Server                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            BlockMind Fabric Mod (Java)                 │  │
│  │                                                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Trình thu │ │Trình thực│ │Trình lắng│ │Baritone  │ │  │
│  │  │thập trạng│ │thi hành  │ │nghe sự   │ │Tìm đường │ │  │
│  │  │thái      │ │động      │ │kiện      │ │(tùy chọn)│ │  │
│  │  │Khối/var  │ │Di chuyển/│ │Trò chuyện│ │          │ │  │
│  │  │tử/túi đồ/│ │đào/đặt/  │ │sát thương│ │          │ │  │
│  │  │thế giới  │ │tấn công  │ │thay đổi  │ │          │ │  │
│  │  │          │ │          │ │khối      │ │          │ │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │  │
│  │       └─────────────┼────────────┼────────────┘       │  │
│  │               HTTP API :25580 + WebSocket              │  │
│  └─────────────────────────────┼──────────────────────────┘  │
└────────────────────────────────┼─────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────┐
│                  BlockMind Python Backend                     │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Kiến trúc Đôi Agent                      │  │
│  │  ┌─────────────────┐  ┌────────────────────────────┐  │  │
│  │  │ Agent Chính     │  │ Agent Thao tác             │  │  │
│  │  │ (Trò chuyện)    │  │ (Thực thi, không trạng    │  │  │
│  │  │ Ngữ cảnh bền    │  │ thái)                      │  │  │
│  │  │ vững            │  │ Ngữ cảnh mới mỗi lần      │  │  │
│  │  │ Nhận diện ý định│  │ Ghép/Tạo/Thực thi Skill   │  │  │
│  │  └────────┬────────┘  └─────────────┬──────────────┘  │  │
│  └───────────┼─────────────────────────┼─────────────────┘  │
│              │                         │                     │
│  ┌───────────▼─────────────────────────▼─────────────────┐  │
│  │               🧠 Hệ thống Ghi nhớ (GameMemory)       │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │Ghi nhớ   │ │Ghi nhớ   │ │Ghi nhớ   │ │Ghi nhớ   │ │  │
│  │  │Không gian│ │Đường dẫn │ │Chiến lược│ │Người chơi│ │  │
│  │  │Vùng bảo  │ │Đường thành│ │Chiến lược│ │Vị trí nhà│ │  │
│  │  │vệ công   │ │công cache│ │thành công│ │Sở thích  │ │  │
│  │  │trình     │ │Blacklist │ │Bài học   │ │Lịch sử   │ │  │
│  │  │Vùng nguy │ │thất bại  │ │thất bại  │ │tương tác │ │  │
│  │  │hiểm      │ │Thống kê  │ │Tag ngữ   │ │          │ │  │
│  │  │Tài nguyên│ │tỷ lệ     │ │cảnh      │ │          │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │  │
│  │              JSON vĩnh viễn (data/memory/)             │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │ Tiêm                          │
│  ┌──────────┐ ┌──────────────▼──────┐ ┌──────────────────┐  │
│  │ Skill    │ │Điều hướng Thông minh│ │Tầng Quyết định AI│  │
│  │Motor     │ │Ghi nhớ→Cache→       │ │Tiêm Ngữ cảnh     │  │
│  │DSL phân  │ │Baritone→A*→Tự học  │ │Ghi nhớ           │  │
│  │tích/equy │ │                     │ │provider.py       │  │
│  │thi       │ │                     │ │                   │  │
│  └──────────┘ └─────────────────────┘ └──────────────────┘  │
│  ┌──────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │Kiểm tra  │ │Giám sát      │ │ WebUI (Miuix Console)   │ │
│  │Bảo mật   │ │Sức khỏe      │ │ Giao diện tối/Cấu hình │ │
│  │5 cấp     │ │3 cấp hạ cấp  │ │ model                  │ │
│  │risk      │ │              │ │                         │ │
│  └──────────┘ └──────────────┘ └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Ví dụ về Luồng Dữ liệu

**Điều hướng Thông minh dựa trên Ghi nhớ:**
```
Người chơi nói "về nhà"
  → Agent Chính nhận diện nhiệm vụ [TASK:ve_nha]
  → Agent Thao tác khớp Skill go_home
  → SmartNavigator truy vấn ghi nhớ:
      ✅ Vị trí nhà: (65, 64, -120) từ ghi nhớ người chơi
      ✅ Đường dẫn cache: Đã đi 3 lần, tỷ lệ thành công 100%
      ✅ Vùng bảo vệ công trình: Vùng căn cứ 30 ô cấm phá hủy
      ✅ Vùng nguy hiểm: (80,12,-50) có dung nham
  → Baritone điều hướng:
      GoalBlock(65, 64, -120)
      + exclusion_zones=[vùng bảo vệ căn cứ]
      → Tự động đi vòng, không phá hủy bất kỳ công trình nào
  → Đến nơi: Đường dẫn cache success_count+1
  → Lần sau về nhà: Đi thẳng đường cache, zero Token tiêu hao
```

---

## 🧠 Hệ thống Ghi nhớ

### Kiến trúc Ba lớp Ghi nhớ

| Lớp | Nội dung Lưu trữ | Vĩnh viễn | Ví dụ |
|-----|------------------|----------|-------|
| **Ghi nhớ Không gian** | Vùng bảo vệ công trình, vùng nguy hiểm, điểm tài nguyên, căn cứ | ✅ JSON | "Phạm vi căn cứ: (50-100, 60-80, -150--90)" |
| **Ghi nhớ Đường dẫn** | Cache đường thành công, blacklist đường thất bại, tỷ lệ thành công | ✅ JSON | "Nhà→Hang mỏ: Qua (70,64,-100) tỷ lệ thành công 100%" |
| **Ghi nhớ Chiến lược** | Chiến lược thành công tích lũy, bài học thất bại, tag ngữ cảnh | ✅ JSON | "Khi đào mỏ nên đặt meo trước rồi đào, hiệu quả cao nhất" |
| **Ghi nhớ Người chơi** | Vị trí nhà, công cụ ưa thích, lịch sử tương tác | ✅ JSON | "Nhà của Steve ở (100,64,200)" |
| **Ghi nhớ Thế giới** | Điểm spawn, điểm an toàn, sự kiện quan trọng | ✅ JSON | "Điểm spawn (0,64,0), Danh sách điểm an toàn" |

### Bảo vệ Công trình Tự động

```python
# Đăng ký vùng bảo vệ công trình (cấm AI phá hủy)
memory.register_building("主城", center=(100, 64, 200), radius=30)
# → Khi điều hướng tự động tiêm Baritone exclusion_zones
# → type: "no_break" + "no_place"
# → AI trong vùng bảo vệ không thể phá/đặt khối

# Tự động phát hiện (mỗi 60 giây quét xung quanh)
navigator.auto_detect_and_memorize()
# → Phát hiện khối công trình liên tục → Tự động đăng ký vùng bảo vệ
# → Phát hiện dung nham/lửa → Tự động đăng ký vùng nguy hiểm
# → Phát hiện quặng tập trung → Tự động đăng ký điểm tài nguyên
```

### Cơ chế Cache Đường dẫn

```python
# Lần đầu điều hướng: AI lập kế hoạch + thực thi
result = await navigator.goto(100, 64, 200)
# → Cache đường: success_count=1, success_rate=100%

# Lần thứ hai: Đi thẳng cache
result = await navigator.goto(100, 64, 200)
# → Trúng cache, thực thi trực tiếp, không tính toán

# Đường thất bại: Tự động học
# → fail_count >= 3 → Tự động thêm vào blacklist
# → Lần sau lập kế hoạch lại, không đi đường cũ
```

### Tự động Tích lũy Chiến lược

```python
# Agent Thao tác thực thi thành công tự động ghi lại
memory.record_strategy(
    task_type="mine",
    description="Đặt meo trước rồi đào mỏ",
    action_sequence=[...],
    success=True,
    context_tags=["nighttime", "cave"],
)

# Lần sau cùng loại nhiệm vụ tự động khớp chiến lược tốt nhất
best = memory.get_best_strategy("mine", context_tags=["nighttime"])
# → Trả về chiến lược có tỷ lệ thành công cao nhất
```

### Tiêm Ngữ cảnh Ghi nhớ cho AI

```python
# Mỗi lần AI ra quyết định tự động tiêm ghi nhớ
memory_context = memory.get_ai_context()
# Đầu ra:
# [Hệ thống Ghi nhớ]
# Căn cứ:
#   - Nhà: (50, 64, -100) (bán kính 30)
# Vùng bảo vệ công trình (cấm phá hủy):
#   - 主城: (100, 64, 200) (bán kính 20)
# Vùng nguy hiểm:
#   - Hồ dung nham: (80, 12, -50) (lava)
# Đường đã biết đáng tin cậy: 3 đường
# Chiến lược đã xác minh: 5 chiến lược
```

---

## 🛤️ Điều hướng Thông minh

### Quy trình Điều hướng

```
SmartNavigator.goto(x, y, z)
  │
  ├── 1. Kiểm tra An toàn
  │     └── Đích trong vùng bảo vệ? → Cảnh báo nhưng không từ chối
  │
  ├── 2. Truy vấn Cache Đường dẫn
  │     └── Có cache đáng tin? → Thực thi cache trực tiếp
  │
  ├── 3. Lấy Ngữ cảnh Điều hướng
  │     ├── Vùng loại trừ (vùng bảo vệ công trình)
  │     ├── Vùng nguy hiểm (dung nham, vách đá)
  │     └── Tham chiếu đường đáng tin cậy
  │
  ├── 4. Baritone tìm đường (ưu tiên)
  │     ├── Tiêm exclusion_zones
  │     ├── Tự động đào đường / xây cầu / bơi
  │     └── Tính chi phí rơi / tránh dung nham
  │
  ├── 5. A* tìm đường (dự phòng)
  │     └── A* lưới cơ bản + đánh giá ô có thể đi qua
  │
  └── 6. Ghi nhận Kết quả
        ├── Thành công → cache_path(success=True)
        └── Thất bại → cache_path(success=False) + có thể blacklist
```

### Tích hợp Baritone

| Tính năng | Baritone | A* Cơ bản |
|-----------|----------|-----------|
| Thuật toán tìm đường | A* Cải tiến + heuristic chi phí | A* Tiêu chuẩn |
| Đào đường | ✅ Tự động đào xuyên chướng ngại | ❌ |
| Xây cầu | ✅ Chế độ scaffold | ❌ |
| Bơi | ✅ | ❌ |
| Di chuyển dọc | ✅ Nhảy/thang/leo dây | ⚠️ Chỉ 1 ô |
| Tránh dung nham | ✅ Phạt chi phí | ❌ |
| Chi phí rơi | ✅ Tính vào heuristic | ❌ |
| Vùng loại trừ | ✅ `exclusionAreas` | ❌ |
| **Bảo vệ công trình** | ✅ Tiêm vùng `no_break` | ❌ |

### Loại Vùng Loại trừ

| Loại | Mô tả | Nguồn |
|------|-------|-------|
| `no_break` | Cấm phá khối | Vùng bảo vệ công trình, căn cứ |
| `no_place` | Cấm đặt khối | Vùng bảo vệ công trình |
| `avoid` | Hoàn toàn tránh | Vùng nguy hiểm (dung nham, v.v.) |

---

## 🤖 Kiến trúc Đôi Agent

### Tại sao cần Đôi Agent?

```
Vấn đề Agent đơn:
  Ngữ cảnh trò chuyện + ngữ cảnh thao tác → Token quá tải (>4000/lần)
  Thao tác thất bại ô nhiễm trò chuyện → Trải nghiệm hội thoại kém
  Mỗi thao tác phải mang toàn bộ lịch sử trò chuyện → Lãng phí

Giải pháp Đôi Agent:
  Agent Chính: Chỉ trò chuyện, cửa sổ trượt 20 tin, ~50 Token/lần
  Agent Thao tác: Không trạng thái, ngữ cảnh mới, <1500 Token/lần
```

### Quy trình

```
Tin nhắn người chơi
  → Agent Chính trò chuyện (ngữ cảnh bền vững)
  → Nhận diện thẻ [TASK:xxx]
  → Trích xuất mô tả nhiệm vụ
  → Agent Thao tác thực thi (không trạng thái):
      ├── Ghép Skill
      ├── Tiêm ngữ cảnh ghi nhớ
      ├── L1/L2: Thực thi Skill đã cache
      ├── L3: AI điền mẫu + thực thi
      └── L4: AI suy luận hoàn toàn + thực thi
  → Agent Chính định dạng phản hồi → Người chơi
```

---
## 🚀 Bắt đầu Nhanh

### Yêu cầu Môi trường

| Thành phần | Yêu cầu |
|------------|---------|
| Python | 3.10+ |
| Java | 17+ |
| Minecraft | 1.19.4 - 1.21.4 |
| Fabric Loader | 0.15+ |

---

## 📦 Triển khai Một chạm

### Tải về

Tải từ [GitHub Releases](https://github.com/bmbxwbh/BlockMind/releases/latest):

| Tệp | Mô tả |
|-----|-------|
| `blockmind-mod-1.0.0.jar` | Fabric Mod (đặt vào thư mục mods/ của server) |
| `Source code` (zip/tar) | Mã nguồn đầy đủ |

### Khởi động Một chạm Linux / macOS

```bash
# Clone
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

# Khởi động một chạm (tự động cài phụ thuộc + MC server + BlockMind + WebUI)
chmod +x start.sh
./start.sh
```

> `start.sh` tự động: Kiểm tra Python/Java → Cài phụ thuộc → Quét MC server đã có → Chọn phiên bản cài → Khởi động tất cả

### Khởi động Một chạm Windows

```cmd
:: Clone (hoặc tải zip giải nén)
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

:: Cài đặt một chạm
install.bat

:: Khởi động một chạm (MC server + BlockMind + WebUI)
start_all.bat
```

> Xem chi tiết tại [Hướng dẫn Triển khai Windows](docs/WINDOWS.md)

### Triển khai Docker

```bash
# Kéo image
docker pull ghcr.io/bmbxwbh/blockmind:latest

# Tải mẫu cấu hình
wget https://raw.githubusercontent.com/bmbxwbh/BlockMind/main/config.example.yaml -O config.yaml
# Chỉnh sửa config.yaml điền cấu hình model AI của bạn

# Khởi động
docker run -d \
  --name blockmind \
  -p 19951:19951 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v blockmind-data:/data \
  ghcr.io/bmbxwbh/blockmind:latest
```

Hoặc dùng docker-compose:

```bash
git clone https://github.com/bmbxwbh/BlockMind.git && cd BlockMind
cp config.example.yaml config.yaml
# Chỉnh sửa config.yaml
docker compose up -d
```

```bash
# Xem nhật ký
docker compose logs -f blockmind
# Dừng
docker compose down
```

### Cấu hình

Chỉnh sửa `config.yaml`:

```yaml
ai:
  main_agent:
    provider: "openai"          # openai hoặc anthropic
    api_key: "sk-your-key"
    model: "gpt-4o"             # Tên model của bạn
    base_url: ""                # Địa chỉ API tùy chỉnh (tùy chọn)

webui:
  enabled: true
  port: 19951
  auth:
    password: "your-password"   # Mật khẩu đăng nhập WebUI
```

Sau khi khởi động truy cập `http://localhost:19951` để vào bảng điều khiển.

---

## 🔌 Fabric Mod API

### Truy vấn Trạng thái

| Endpoint | Phương thức | Mô tả |
|----------|-------------|-------|
| `/health` | GET | Kiểm tra sức khỏe |
| `/api/status` | GET | Trạng thái người chơi |
| `/api/world` | GET | Trạng thái thế giới |
| `/api/inventory` | GET | Thông tin túi đồ |
| `/api/entities?radius=32` | GET | Thực thể lân cận |
| `/api/blocks?radius=16` | GET | Khối lân cận |

### Thực hiện Hành động

| Endpoint | Phương thức | Mô tả |
|----------|-------------|-------|
| `/api/move` | POST | Di chuyển đến tọa độ |
| `/api/dig` | POST | Đào khối |
| `/api/place` | POST | Đặt khối |
| `/api/attack` | POST | Tấn công thực thể |
| `/api/eat` | POST | Ăn |
| `/api/look` | POST | Nhìn đến tọa độ |
| `/api/chat` | POST | Gửi tin nhắn chat |

### Quy hoạch Đường đi

| Endpoint | Phương thức | Mô tả |
|----------|-------------|-------|
| `/api/pathfind` | POST | Điều hướng đường đi (Baritone/A*) |
| `/api/pathfind/stop` | POST | Dừng điều hướng |
| `/api/pathfind/status` | GET | Trạng thái điều hướng |

### Đẩy Sự kiện

Mod đẩy sự kiện qua WebSocket:
- `player_damaged` — Người chơi bị thương
- `entity_attack` — Bị tấn công
- `health_low` — Máu thấp
- `inventory_full` — Túi đồ đầy
- `block_broken` — Đào khối hoàn tất

---

## 📝 Hệ thống Skill DSL

### Phân cấp Nhiệm vụ

| Cấp | Loại | Ví dụ | Chiến lược Cache |
|-----|------|-------|-----------------|
| L1 | Nhiệm vụ cố định | "Về nhà" | Thực thi trực tiếp |
| L2 | Nhiệm vụ có tham số | "Đào 10 viên kim cương" | Cache có tham số |
| L3 | Nhiệm vụ mẫu | "Xây một nơi trú ẩn" | Khớp mẫu |
| L4 | Nhiệm vụ động | "Giúp tôi đánh bại Rồng Ender" | AI suy luận |

### Ví dụ Skill YAML

```yaml
skill_id: mine_diamonds
name: "Đào kim cương"
level: L2
parameters:
  count: {type: int, default: 10, min: 1, max: 64}
steps:
  - action: pathfind
    target: {y: -59}
    note: "Đến tầng kim cương"
  - action: dig_loop
    block: diamond_ore
    count: ${count}
  - action: pathfind
    target: home
    note: "Quay về căn cứ"
```

---

## 🛡️ Hệ thống Bảo mật

| Tầng | Cơ chế | Mô tả |
|------|--------|-------|
| L1 | Đánh giá Rủi ro | Mỗi hành động chấm điểm 0-100 |
| L2 | Xác nhận Thao tác | Rủi ro cao cần xác nhận |
| L3 | Can thiệp Khẩn cấp | Người chơi có thể ngắt AI bất cứ lúc nào |
| L4 | Nhật ký Kiểm toán | Mọi thao tác có thể truy vết |
| L5 | Giới hạn Vùng An toàn | Giới hạn phạm vi phá/đặt |

---

## 🖥️ Bảng điều khiển WebUI

Sau khi khởi động truy cập `http://localhost:19951`, hỗ trợ:

- 📊 Dashboard — Giám sát trạng thái thời gian thực
- 🛠️ Quản lý Skill — Chỉnh sửa YAML trực tuyến
- 🧠 Hệ thống Ghi nhớ — Xem/Dọn/Sao lưu
- 🤖 Cấu hình Model — Chuyển đổi model AI nóng
- 💬 Bảng lệnh — Lệnh ngôn ngữ tự nhiên
- 📋 Hàng đợi Nhiệm vụ — Xem trạng thái thực thi
- 📝 Trung tâm Nhật ký — Luồng nhật ký thời gian thực

---

## ❓ Câu hỏi Thường gặp

**Q: Có phải cài Baritone không?**
A: Không bắt buộc. Baritone là phụ thuộc tùy chọn, khi không có tự động chuyển sang A* cơ bản di chuyển đường thẳng.

**Q: Dữ liệu ghi nhớ lưu ở đâu?**
A: Trong thư mục `data/memory/`, 5 tệp JSON, được giữ liên phiên.

**Q: Bảo vệ công trình có hiệu lực thế nào?**
A: Hai cách: ① Đăng ký thủ công ② Tự động phát hiện (mỗi 60 giây quét).

**Q: Hỗ trợ những nhà cung cấp AI nào?**
A: Định dạng tương thích OpenAI (bao gồm DeepSeek/OpenRouter/MiMo, v.v.) + Định dạng Anthropic.

**Q: Image Docker lớn bao nhiêu?**
A: Khoảng 200MB, xây dựng nhiều giai đoạn dựa trên python:3.11-slim.

---

## 🗺️ Lộ trình

### v3.0 (Hiện tại) ✅
- [x] Hệ thống ghi nhớ ba lớp (Không gian/Đường dẫn/Chiến lược)
- [x] Điều hướng thông minh (Ghi nhớ hỗ trợ + Tích hợp Baritone)
- [x] Kiến trúc Đôi Agent (Cô lập Trò chuyện/Thao tác)
- [x] Bảo vệ công trình tự động
- [x] Miuix Console WebUI
- [x] Triển khai Một chạm Windows/Linux
- [x] Image Docker + Tự động xuất bản GHCR
- [x] GitHub Actions CI/CD

### v3.1 (Kế hoạch)
- [ ] Đa phương thức đầu vào (phân tích ảnh chụp màn hình)
- [ ] Chợ Skill (Nhập/Xuất)
- [ ] Hợp tác nhiều người chơi
- [ ] Tương tác giọng nói

---

## 📄 Giấy phép

MIT License. Xem chi tiết tại [LICENSE](LICENSE).
