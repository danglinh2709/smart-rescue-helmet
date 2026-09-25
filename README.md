# Smart Rescue Helmet

Smart Rescue Helmet là nguyên mẫu hệ thống giám sát an toàn cho mũ cứu hộ thông minh. Dự án được phát triển theo hướng **software-first**: simulator thay thế thiết bị ESP32-S3 trong giai đoạn phát triển, nhưng vẫn sử dụng cùng MQTT contract mà phần cứng thật sẽ dùng sau này.

Hệ thống hiện có simulator Python và Unity, MQTT broker, FastAPI backend, PostgreSQL, Safety Engine, WebSocket realtime và dashboard React.

## Kiến trúc hệ thống

```text
Python Simulator / Unity Simulator
                 |
                 | MQTT
                 v
        Eclipse Mosquitto
                 |
                 v
          FastAPI Backend
          |      |       |
          |      |       +--> WebSocket realtime
          |      +----------> Safety Engine
          +-----------------> PostgreSQL
                                  |
                                  v
                           React Dashboard
```

Backend là nguồn sự thật về mức rủi ro và sự kiện an toàn. Simulator chỉ gửi dữ liệu cảm biến; backend tự đánh giá `NORMAL`, `WARNING` hoặc `CRITICAL` và tự tạo event tương ứng.

## Chức năng hiện tại

### Python device simulator

Python simulator đóng vai trò một ESP32-S3 ảo và hỗ trợ:

- Sinh dữ liệu nhiệt độ, CO, IMU, chuyển động, pin và trạng thái kết nối.
- Mô phỏng ngã, bất động và nút SOS.
- Publish `telemetry`, `status` và `health` theo chu kỳ cấu hình.
- Validate payload bằng JSON Schema trước khi publish.
- Cảnh báo cục bộ độc lập với backend bằng LED, còi và rung ảo.
- Có các scenario: normal, nhiệt độ cao, CO cao, ngã, ngã kèm bất động, bất động, SOS và pin yếu.

Chương trình mặc định sử dụng `NormalScenario`. Để chạy scenario khác, thay lựa chọn scenario trong `simulator/main.py` rồi build lại service simulator.

### MQTT và shared contract

Mosquitto nhận dữ liệu theo namespace `helmet/{device_id}`:

| Topic | Nội dung | QoS của Python simulator |
|---|---|---:|
| `helmet/{device_id}/telemetry` | Dữ liệu cảm biến và trạng thái người đội | 0 |
| `helmet/{device_id}/status` | Trạng thái logic hiện tại của thiết bị | 1 |
| `helmet/{device_id}/health` | Pin, uptime, kết nối và tình trạng sensor | 1 |
| `helmet/{device_id}/event` | Topic tương thích contract; backend không tin event từ simulator | 1 |

Các Pydantic schema của backend là nguồn định nghĩa dữ liệu. JSON Schema dùng chung được lưu trong `shared/contracts/`.

Backend kiểm tra `device_id` trong topic phải trùng với payload, bỏ qua message sai contract và tự reconnect khi MQTT broker bị gián đoạn.

### Backend Safety Engine

Safety Engine đánh giá mỗi telemetry message theo các ngưỡng sau:

| Điều kiện | Mức rủi ro |
|---|---|
| Không có điều kiện nguy hiểm | `NORMAL` |
| Pin ≤ 20% | `WARNING` |
| Nhiệt độ từ 50°C đến dưới 60°C | `WARNING` |
| CO từ 50 đến dưới 100 | `WARNING` |
| SOS được nhấn | `CRITICAL` |
| Phát hiện ngã | `CRITICAL` |
| Ngã và bất động | `CRITICAL` |
| Nhiệt độ ≥ 60°C | `CRITICAL` |
| CO ≥ 100 | `CRITICAL` |

Khi có nhiều điều kiện cùng lúc, Safety Engine lưu toàn bộ nguyên nhân. Chỉ cần một nguyên nhân critical thì kết quả cuối cùng là `CRITICAL`.

Safety Engine có thể sinh các event:

- `TEMPERATURE_HIGH`
- `CO_HIGH`
- `FALL_DETECTED`
- `SOS_PRESSED`
- `LOW_BATTERY`

Trạng thái actuator tương ứng:

| Risk | LED | Còi | Rung |
|---|---|---|---|
| `NORMAL` | Xanh | Tắt | Tắt |
| `WARNING` | Vàng | Tắt | Tắt |
| `CRITICAL` | Đỏ | Bật | Bật |

### Database và lịch sử

Backend sử dụng PostgreSQL để lưu:

- Thiết bị.
- Telemetry.
- Trạng thái thiết bị.
- Device health.
- Safety event và event chuyển trạng thái kết nối.

Các bảng được khởi tạo khi backend bắt đầu chạy.

### Realtime và độ tin cậy

Backend cung cấp WebSocket tại `/ws` và broadcast:

- Trạng thái ban đầu của tất cả thiết bị khi client kết nối.
- Telemetry, status, health và event mới.
- Snapshot trạng thái mới nhất của từng thiết bị.

Backend ghi nhận `last_seen` của mỗi thiết bị. Nếu không nhận được message hợp lệ trong thời gian cấu hình, thiết bị được chuyển sang `OFFLINE` và hệ thống tạo event `DEVICE_OFFLINE`. Khi dữ liệu xuất hiện trở lại, thiết bị chuyển sang `ONLINE` và tạo event `MQTT_RECONNECTED`.

### Dashboard

Dashboard React gồm các màn hình:

- **Overview**: tổng số thiết bị, số thiết bị online, warning và critical.
- **Devices**: bảng trạng thái, nhiệt độ, CO, pin và lần cập nhật cuối.
- **Device detail**: telemetry, IMU, health, sensor health và actuator.
- **Events**: danh sách event và cảnh báo critical mới nhất.
- **History**: truy vấn lịch sử telemetry, event hoặc health theo thiết bị.
- **System**: trạng thái backend, WebSocket, MQTT và Wi-Fi.

Dashboard tải dữ liệu ban đầu qua REST API, nhận cập nhật qua WebSocket và tự reconnect WebSocket sau khi mất kết nối.

### Unity simulator

`unity-simulator/` cung cấp một môi trường mô phỏng trực quan:

- Điều khiển nhân vật cứu hộ.
- Chuyển camera người thứ nhất và command center bằng phím `C`.
- Vùng nguy hiểm làm tăng nhiệt độ hoặc CO cục bộ.
- LED, còi và rung ảo theo đánh giá an toàn cục bộ.
- MQTT publisher và reconnect tự động.
- Bản build Windows nằm trong `unity-simulator/Build/`.

Unity simulator hiện vẫn là prototype. Telemetry MQTT của Unity còn dùng payload normal cố định; một số scenario đã khai báo nhưng chưa nối đầy đủ vào trạng thái gửi lên backend. Python simulator hiện là nguồn mô phỏng đầy đủ và ổn định hơn.

## REST API

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/` | Thông tin backend |
| `GET` | `/health` | Healthcheck backend |
| `GET` | `/api/v1/devices` | Runtime state của tất cả thiết bị |
| `GET` | `/api/v1/telemetry` | Toàn bộ lịch sử telemetry |
| `GET` | `/api/v1/telemetry/{device_id}` | Telemetry của một thiết bị |
| `GET` | `/api/v1/telemetry/latest/{device_id}` | Telemetry mới nhất |
| `GET` | `/api/v1/events` | Toàn bộ event |
| `GET` | `/api/v1/events/{device_id}` | Event của một thiết bị |
| `GET` | `/api/v1/events/latest/{device_id}` | Event mới nhất |
| `GET` | `/api/v1/health/history` | Toàn bộ lịch sử health |
| `GET` | `/api/v1/health/history/{device_id}` | Health của một thiết bị |
| `GET` | `/api/v1/health/history/latest/{device_id}` | Health mới nhất |
| `WS` | `/ws` | Kênh cập nhật realtime |

Swagger UI có tại <http://localhost:8000/docs> khi backend đang chạy.

## Cấu trúc dự án

```text
smart-rescue-helmet/
|-- backend/             FastAPI, MQTT subscriber, Safety Engine và database
|-- frontend/            React, TypeScript và Vite dashboard
|-- simulator/           Python device simulator
|-- unity-simulator/     Môi trường mô phỏng trực quan bằng Unity
|-- shared/              MQTT contract, enum và JSON Schema dùng chung
|-- mosquitto/           Cấu hình Eclipse Mosquitto
|-- tests/               Tài liệu và kiểm thử tích hợp
|-- docker-compose.yml
|-- .env.example
`-- README.md
```

## Yêu cầu

- Docker Desktop có Docker Compose.
- Git.
- Unity Editor chỉ cần thiết khi muốn chỉnh sửa hoặc build lại Unity simulator.

Không cần cài Python, Node.js hay PostgreSQL trên máy nếu chạy toàn bộ hệ thống bằng Docker Compose.

## Chạy hệ thống

### 1. Tạo file cấu hình

PowerShell:

```powershell
Copy-Item .env.example .env
```

Bash:

```bash
cp .env.example .env
```

### 2. Build và khởi động

```bash
docker compose up --build
```

Các service được khởi động:

- `postgres`
- `mosquitto`
- `backend`
- `frontend`
- `simulator`

### 3. Truy cập

| Service | Địa chỉ |
|---|---|
| Dashboard | <http://localhost:5173> |
| Backend | <http://localhost:8000> |
| Backend health | <http://localhost:8000/health> |
| Swagger UI | <http://localhost:8000/docs> |
| MQTT/TCP | `localhost:1883` |
| MQTT/WebSocket | `localhost:9001` |
| PostgreSQL | `localhost:5432` |

### 4. Theo dõi MQTT

```bash
docker compose exec mosquitto mosquitto_sub -h localhost -t "helmet/#" -v
```

### 5. Dừng hệ thống

```bash
docker compose down
```

Chỉ thêm `-v` nếu muốn xóa cả PostgreSQL named volume và toàn bộ dữ liệu đã lưu:

```bash
docker compose down -v
```

## Cấu hình môi trường

Các biến chính trong `.env.example`:

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `SIMULATOR_DEVICE_ID` | `FF01` | Mã thiết bị simulator |
| `SIMULATOR_TELEMETRY_INTERVAL` | `1` | Chu kỳ telemetry, tính bằng giây |
| `SIMULATOR_STATUS_INTERVAL` | `2` | Chu kỳ status |
| `SIMULATOR_HEALTH_INTERVAL` | `5` | Chu kỳ health |
| `SIMULATOR_MQTT_PUBLISH_ENABLED` | `true` | Bật hoặc tắt publish MQTT |
| `DEVICE_OFFLINE_TIMEOUT_SECONDS` | `10` | Thời gian chờ trước khi đánh dấu offline |
| `DEVICE_OFFLINE_CHECK_INTERVAL_SECONDS` | `2` | Chu kỳ kiểm tra thiết bị offline |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend URL dùng bởi dashboard |
| `VITE_WS_URL` | `ws://localhost:8000/ws` | WebSocket URL dùng bởi dashboard |

## Chạy kiểm thử

Backend và simulator dùng `pytest`. Backend cần được chạy từ thư mục
`backend/` và cần một `DATABASE_URL` hợp lệ ngay từ lúc import ứng dụng.

PowerShell:

```powershell
Set-Location backend
$env:DATABASE_URL = "sqlite:///:memory:"
python -m pytest tests
Set-Location ..
python -m pytest simulator/tests
```

Bash:

```bash
(cd backend && DATABASE_URL=sqlite:///:memory: python -m pytest tests)
python -m pytest simulator/tests
```

Frontend dùng Vitest:

```bash
cd frontend
npm test
```

Build kiểm tra frontend:

```bash
cd frontend
npm run build
```

Unity có EditMode tests trong `unity-simulator/Assets/Tests/EditMode/`.

## Contract và tài liệu liên quan

- `shared/README.md`: quy tắc chung của wire contract.
- `shared/mqtt_topics.md`: MQTT topic contract.
- `shared/enums.md`: enum dùng chung.
- `shared/contracts/`: JSON Schema cho telemetry, status, health và event.
- `docs/superpowers/specs/2026-09-25-unity-rescue-simulator-design.md`: thiết kế Unity simulator.

## Giới hạn hiện tại

- Chưa tích hợp ESP32-S3 và cảm biến vật lý.
- Chưa có đăng nhập hoặc phân quyền người dùng.
- Chưa gửi cảnh báo qua SMS, email hoặc push notification.
- Chưa có GPS, bản đồ, camera, AI hoặc điều hướng cứu hộ.
- Chưa điều khiển thiết bị từ dashboard.
- MQTT đang bật anonymous access để phục vụ local development.
- Unity simulator chưa đồng bộ đầy đủ trạng thái mô phỏng vào payload MQTT.

## Lưu ý bảo mật

Cấu hình Mosquitto hiện dùng `allow_anonymous true` để thuận tiện trong môi trường local. Trước khi triển khai thực tế cần bổ sung authentication, authorization, TLS, quản lý secret và chính sách truy cập cho database, API, MQTT và WebSocket.
