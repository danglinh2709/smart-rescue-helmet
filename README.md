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
