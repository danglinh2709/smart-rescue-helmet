# Smart Rescue Helmet V1

Smart Rescue Helmet V1 là nguyên mẫu hệ thống hỗ trợ an toàn và cứu hộ cho mũ bảo hộ thông minh. Dự án được phát triển theo hướng **software-first**: kiểm chứng kiến trúc phần mềm bằng dữ liệu giả lập trước, sau đó thay simulator bằng phần cứng thật mà không phải thiết kế lại backend, database, API hay giao diện.

## Software-first architecture

Kiến trúc phần mềm mục tiêu:

```text
Python Simulator
       |
Safety Engine
       |
MQTT Broker -> FastAPI Backend -> PostgreSQL
                     |
                  WebSocket
                     |
              React Dashboard
```

Milestone 3 bổ sung Python Simulator đóng vai virtual ESP32-S3, chạy NORMAL scenario và publish telemetry/status/health thật qua Mosquitto. **Backend chưa subscribe MQTT; Safety Engine, event runtime, WebSocket nghiệp vụ và Dashboard nghiệp vụ chưa được triển khai.**

## Kiến trúc phần cứng dự kiến

Khi có phần cứng, ESP32-S3 sẽ thay thế Python Simulator và sử dụng cùng MQTT contract:

```text
MPU6050 / DS18B20 / MQ-7 / SOS Button
                    |
                 ESP32-S3
                    |
               MQTT Broker
                    |
             FastAPI Backend
                    |
               PostgreSQL
                    |
             React Dashboard
```

## Project structure

```text
smart-rescue-helmet/
|-- backend/
|   |-- app/
|   |   |-- core/
|   |   |   |-- enums.py
|   |   |   `-- mqtt_topics.py
|   |   |-- schemas/
|   |   |   |-- common.py
|   |   |   |-- telemetry.py
|   |   |   |-- event.py
|   |   |   |-- device_status.py
|   |   |   `-- device_health.py
|   |   |-- __init__.py
|   |   `-- main.py
|   |-- scripts/
|   |   `-- export_json_schemas.py
|   |-- tests/
|   |   |-- core/
|   |   |-- schemas/
|   |   |-- test_json_schema_export.py
|   |   `-- test_main.py
|   |-- Dockerfile
|   |-- requirements.txt
|   `-- requirements-dev.txt
|-- frontend/
|   |-- src/
|   |-- Dockerfile
|   |-- package.json
|   `-- vite.config.ts
|-- simulator/
|   |-- contracts/
|   |-- mqtt/
|   |-- scenarios/
|   |-- sensors/
|   |-- tests/
|   |-- config.py
|   |-- main.py
|   |-- Dockerfile
|   |-- requirements.txt
|   `-- README.md
|-- shared/
|   |-- contracts/
|   |-- enums.md
|   |-- mqtt_topics.md
|   `-- README.md
|-- mosquitto/
|   |-- config/mosquitto.conf
|   |-- data/.gitkeep
|   `-- log/.gitkeep
|-- tests/
|   `-- README.md
|-- .env.example
|-- .gitignore
|-- docker-compose.yml
`-- README.md
```

## Yêu cầu

- Docker Desktop
- Docker Compose
- Git

## Chạy hệ thống

PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Bash:

```bash
cp .env.example .env
docker compose up --build
```

## Quan sát MQTT Simulator

Simulator publish kịch bản NORMAL với interval cấu hình trong `.env`. Có thể quan sát trực tiếp bằng Mosquitto client trong container:

```bash
docker compose exec mosquitto mosquitto_sub -h localhost -t "helmet/#" -v
```

Các topic hiện được publish:

- `helmet/FF01/telemetry` mỗi 1 giây, QoS 0.
- `helmet/FF01/status` mỗi 2 giây, QoS 1.
- `helmet/FF01/health` mỗi 5 giây, QoS 1.

NORMAL scenario không publish `helmet/FF01/event`. Backend chưa nhận hoặc lưu các message này trong Milestone 3.

## Dừng hệ thống

```bash
docker compose down
```

Thêm `-v` chỉ khi bạn chủ động muốn xóa cả dữ liệu PostgreSQL trong named volume.

## Service URLs

| Service | URL / address |
|---|---|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| Backend health | http://localhost:8000/health |
| API docs | http://localhost:8000/docs |
| MQTT | localhost:1883 |
| MQTT over WebSocket | localhost:9001 |
| PostgreSQL | localhost:5432 |

## Cảnh báo bảo mật MQTT

Mosquitto đang bật `allow_anonymous true` để thuận tiện cho môi trường **local development**. Môi trường production sau này bắt buộc phải bật authentication, phân quyền và TLS.

## Milestone hiện tại

Milestone 3 — Python Device Simulator + NORMAL Scenario + MQTT Publisher:

- FastAPI tối thiểu với `/` và `/health`
- PostgreSQL 16 có persistent volume và healthcheck
- Eclipse Mosquitto 2 cho MQTT/TCP và MQTT/WebSocket
- React + TypeScript + Vite với trang khởi tạo tĩnh
- Docker Compose chạy năm service từ thư mục root
- Pydantic v2 là source of truth cho telemetry, event, status và health
- MQTT topic helpers và tài liệu wire contract
- JSON Schema được generate vào `shared/contracts/`
- Python Simulator tạo sensor data NORMAL deterministic
- Payload được validate bằng shared JSON Schema trước mỗi publish
- Mosquitto nhận telemetry, status và health từ virtual device

Không có Backend MQTT subscriber, event runtime, Safety Engine, database nghiệp vụ, WebSocket realtime, Dashboard nghiệp vụ, AI, camera hoặc navigation trong milestone này.
##
##
##
## Milestone 4 – MQTT → Backend

FastAPI Backend được mở rộng để hoạt động như một MQTT Subscriber. Backend kết nối tới Eclipse Mosquitto, subscribe các MQTT topics đã định nghĩa trong Shared Contract và tiếp nhận dữ liệu do Python Simulator publish.

Mỗi MQTT message sau khi nhận sẽ được parse từ JSON và validate bằng Pydantic v2 nhằm đảm bảo đúng định dạng contract. Sau khi xác thực thành công, Backend cập nhật Runtime State của từng thiết bị trong bộ nhớ, bao gồm dữ liệu telemetry, status, health và event (nếu có).

Milestone này chưa lưu dữ liệu vào PostgreSQL, chưa triển khai Safety Engine, chưa phát WebSocket và chưa có Dashboard nghiệp vụ. Mục tiêu là xây dựng pipeline ổn định từ MQTT đến Backend làm nền tảng cho các milestone tiếp theo.

## Software Architecture
```text
Python Simulator
        │
        ▼
MQTT Broker (Mosquitto)
        │
        ▼
FastAPI MQTT Subscriber
        │
        ▼
JSON Parser
        │
        ▼
Pydantic Validation
        │
        ▼
Device Runtime State (Memory)
```

## Data Flow
```text
Python Simulator
        │
Publish telemetry / status / health
        │
        ▼
Mosquitto Broker
        │
        ▼
Backend Subscribe
        │
        ▼
Parse JSON
        │
        ▼
Validate bằng Pydantic
        │
        ▼
Update Runtime State
        │
        ▼
REST API
(/api/v1/devices)
```

## MQTT Topics
|Topic | Nội dung|
| --- | --- |
|helmet/+/telemetry | Dữ liệu cảm biến |
|helmet/+/status | Trạng thái thiết bị |
|helmet/+/health | Thông tin sức khỏe thiết bị |
|helmet/+/event | Sự kiện từ thiết bị |

## Chức năng hoàn thành
- FastAPI kết nối tới Eclipse Mosquitto.
- Backend subscribe các MQTT topics theo Shared Contract.
- Nhận MQTT message từ Python Simulator.
- Parse MQTT payload dạng JSON.
- Validate message bằng Pydantic v2.
- Cập nhật Runtime State của từng thiết bị.
- Hỗ trợ telemetry, status, health và event messages.
- Cung cấp REST API /api/v1/devices để xem Runtime State hiện tại.
- Ghi log khi nhận message hợp lệ hoặc khi validation thất bại.
- Hỗ trợ tự động reconnect khi MQTT Broker bị ngắt kết nối.
## Ví dụ Runtime State

 Sau khi Simulator publish dữ liệu, truy cập:

http://localhost:8000/api/v1/devices

Ví dụ kết quả:

{
  "count": 1,
  "devices": {
    "FF01": {
      "telemetry": { ... },
      "status": { ... },
      "health": { ... },
      "event": null
    }
  }
}

## Trong NORMAL Scenario, trường event có giá trị null vì Simulator chưa phát sinh sự kiện.
```text
Project Structure (bổ sung)
backend/
│
├── app/
│   ├── mqtt/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── subscriber.py
│   │   └── handlers.py
│   │
│   ├── services/
│   │   └── device_state.py
│   │
│   ├── schemas/
│   └── main.py
```
## Không nằm trong Milestone 4

Các chức năng sau chưa được triển khai:

- Lưu dữ liệu vào PostgreSQL.
- Lưu lịch sử Telemetry.
- Lưu lịch sử Event.
- Rule-based Safety Engine.
- Sinh cảnh báo (Alert).
- WebSocket Realtime.
- Dashboard nghiệp vụ.
- Hardware Integration.
## Milestone hiện tại

Milestone 4 — MQTT Subscriber + Backend Runtime

- FastAPI kết nối tới Eclipse Mosquitto.
- Subscribe telemetry, status, health và event topics.
- Parse JSON payload.
- Validate bằng Pydantic v2.
- Cập nhật Runtime State của thiết bị.
- Cung cấp REST API /api/v1/devices.
- Ghi log khi nhận message hoặc khi validation thất bại.
- Hỗ trợ reconnect MQTT tự động.
- Chưa lưu Database.
- Chưa Safety Engine.
- Chưa WebSocket.
- Chưa Dashboard.

##
##
# Milestone 5 – Database & History
FastAPI Backend được mở rộng để lưu trữ dữ liệu vào PostgreSQL thay vì chỉ giữ trong Runtime Memory như Milestone 4. Mỗi khi Backend nhận dữ liệu từ MQTT và hoàn thành bước validation, dữ liệu sẽ được ghi vào cơ sở dữ liệu để phục vụ việc lưu trữ và truy vấn lịch sử.

Bên cạnh đó, hệ thống xây dựng các REST API cho phép lấy lịch sử Telemetry, Event và Health Status của từng thiết bị hoặc toàn bộ hệ thống.

Milestone này chưa triển khai Safety Engine, Alert, WebSocket Realtime và Dashboard. Mục tiêu là hoàn thiện tầng lưu trữ dữ liệu và cung cấp API truy vấn lịch sử làm nền tảng cho các milestone tiếp theo.

---

## Software Architecture

```text
Python Simulator
        │
        ▼
MQTT Broker (Mosquitto)
        │
        ▼
FastAPI MQTT Subscriber
        │
        ▼
Pydantic Validation
        │
        ▼
PostgreSQL Database
        │
        ▼
History REST API
```

---

## Data Flow

```text
Python Simulator
        │
Publish telemetry / status / health / event
        │
        ▼
Mosquitto Broker
        │
        ▼
Backend Subscribe
        │
        ▼
Validate bằng Pydantic
        │
        ▼
Lưu vào PostgreSQL
        │
        ▼
REST API
(/api/v1/telemetry)
/api/v1/events
/api/v1/health/history
```

---

## Database

Hệ thống sử dụng PostgreSQL để lưu trữ dữ liệu lịch sử.

Các bảng chính:

- telemetry
- events
- health_status

---

## REST APIs

### Telemetry

- GET `/api/v1/telemetry`
- GET `/api/v1/telemetry/{device_id}`
- GET `/api/v1/telemetry/latest/{device_id}`

### Events

- GET `/api/v1/events`
- GET `/api/v1/events/{device_id}`
- GET `/api/v1/events/latest/{device_id}`

### Health

- GET `/api/v1/health/history`
- GET `/api/v1/health/history/{device_id}`
- GET `/api/v1/health/history/latest/{device_id}`

---

## Chức năng hoàn thành

- Tích hợp PostgreSQL vào Backend.
- Tự động tạo các bảng dữ liệu khi khởi động hệ thống.
- Lưu dữ liệu Telemetry vào PostgreSQL.
- Lưu dữ liệu Event vào PostgreSQL.
- Lưu dữ liệu Health Status vào PostgreSQL.
- Xây dựng REST API truy vấn lịch sử dữ liệu.
- Hỗ trợ lấy dữ liệu mới nhất của từng thiết bị.
- Tách API thành các Router riêng (`telemetry`, `event`, `health`).
- Kiểm tra API thông qua Swagger UI.


## Không nằm trong Milestone 5

Các chức năng sau chưa được triển khai:

- Rule-based Safety Engine.
- Alert Notification.
- WebSocket Realtime.
- Dashboard nghiệp vụ.
- Hardware Integration.

---

## Milestone hiện tại

**Milestone 5 — Database & History**

- Tích hợp PostgreSQL.
- Lưu Telemetry vào Database.
- Lưu Event vào Database.
- Lưu Health Status vào Database.
- Xây dựng API truy vấn lịch sử.
- Hỗ trợ lấy dữ liệu mới nhất.
- Tách API bằng FastAPI APIRouter.
- Kiểm tra API bằng Swagger UI.
- Chưa triển khai Safety Engine.
- Chưa có Alert.
- Chưa có WebSocket.
- Chưa có Dashboard.