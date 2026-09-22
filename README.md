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

---

# Milestone 6 – Safety Engine & Event Detection

Milestone 6 bổ sung **Rule-based Safety Engine** vào Backend. Mục tiêu của milestone là để Backend tự đánh giá mức độ rủi ro dựa trên dữ liệu Telemetry nhận được từ thiết bị, thay vì tin vào `risk_level` do Simulator gửi lên.

Safety Engine phân tích các thông tin như nhiệt độ, nồng độ CO, trạng thái ngã, trạng thái bất động, nút SOS và mức pin để xác định:

* `NORMAL`
* `WARNING`
* `CRITICAL`

Khi phát hiện điều kiện nguy hiểm, Backend tự tạo Safety Event và lưu Event vào PostgreSQL.

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
Safety Engine
       │
       ├──────────────► Risk Level
       │
       └──────────────► Safety Reasons
                              │
                              ▼
                         Event Creation
                              │
                              ▼
                       PostgreSQL
```

## Safety Rules

Safety Engine sử dụng các ngưỡng hiện tại:

| Điều kiện                    | Mức rủi ro |
| ---------------------------- | ---------- |
| Không có điều kiện nguy hiểm | `NORMAL`   |
| Battery ≤ 20%                | `WARNING`  |
| Temperature ≥ 50°C và < 60°C | `WARNING`  |
| CO ≥ 50 và < 100             | `WARNING`  |
| SOS được nhấn                | `CRITICAL` |
| Phát hiện ngã                | `CRITICAL` |
| Ngã + bất động               | `CRITICAL` |
| Temperature ≥ 60°C           | `CRITICAL` |
| CO ≥ 100                     | `CRITICAL` |

Nếu có nhiều điều kiện cùng xảy ra, các `reasons` được thu thập cùng lúc. Chỉ cần xuất hiện một điều kiện thuộc nhóm Critical thì kết quả cuối cùng là `CRITICAL`.

## Safety Reasons

Safety Engine tạo các reason nội bộ để mô tả nguyên nhân:

| Reason                 | Ý nghĩa                    |
| ---------------------- | -------------------------- |
| `SOS_PRESSED`          | Người dùng nhấn nút SOS    |
| `FALL_DETECTED`        | Phát hiện ngã              |
| `FALL_AND_IMMOBILE`    | Phát hiện ngã và bất động  |
| `HIGH_TEMPERATURE`     | Nhiệt độ cao               |
| `CRITICAL_TEMPERATURE` | Nhiệt độ ở mức nguy hiểm   |
| `HIGH_CO`              | Nồng độ CO cao             |
| `CRITICAL_CO`          | Nồng độ CO ở mức nguy hiểm |
| `LOW_BATTERY`          | Pin thấp                   |

## Data Flow

```text
Telemetry MQTT
      │
      ▼
Pydantic Validation
      │
      ▼
SafetyEngine.evaluate()
      │
      ├── RiskLevel
      │
      └── Reasons
             │
             ├── NORMAL
             │     └── Không tạo Event
             │
             ├── WARNING
             │     └── Tạo Event nếu có reason tương ứng
             │
             └── CRITICAL
                   └── Tạo Critical Event
```

## Backend là nguồn sự thật về Risk

Một nguyên tắc quan trọng được áp dụng từ Milestone 6:

```text
Simulator
    │
    │ telemetry conditions
    ▼
Backend Safety Engine
    │
    ▼
Risk Level
```

Backend **không tin `risk_level` do Simulator quyết định**.

Sau khi validate Telemetry, Backend đưa dữ liệu vào `SafetyEngine`. Kết quả từ Safety Engine được sử dụng để ghi `risk_level` vào Telemetry trước khi lưu Database.

Điều này giúp tách biệt:

* Simulator: tạo dữ liệu và điều kiện giả lập.
* Safety Engine: quyết định mức độ rủi ro.
* Event Service: tạo và lưu Safety Event.

## Event Detection

Safety Event được Backend tạo dựa trên kết quả của Safety Engine.

Các EventType hiện tại:

| Safety Reason          | Event Type         | Severity   |
| ---------------------- | ------------------ | ---------- |
| `SOS_PRESSED`          | `SOS_PRESSED`      | `CRITICAL` |
| `FALL_DETECTED`        | `FALL_DETECTED`    | `CRITICAL` |
| `FALL_AND_IMMOBILE`    | `FALL_DETECTED`    | `CRITICAL` |
| `HIGH_CO`              | `CO_HIGH`          | `WARNING`  |
| `CRITICAL_CO`          | `CO_HIGH`          | `CRITICAL` |
| `HIGH_TEMPERATURE`     | `TEMPERATURE_HIGH` | `WARNING`  |
| `CRITICAL_TEMPERATURE` | `TEMPERATURE_HIGH` | `CRITICAL` |
| `LOW_BATTERY`          | `LOW_BATTERY`      | `WARNING`  |

Nếu Risk Level là `NORMAL`, Backend không tạo Safety Event.

## PostgreSQL

Milestone 6 sử dụng PostgreSQL để lưu:

* Telemetry sau khi được Safety Engine đánh giá.
* Safety Event được Backend tạo.
* Risk Level.
* Safety Reasons trong Event data.

Ví dụ một Telemetry sau khi xử lý:

```json
{
  "device_id": "FF01",
  "temperature": 75,
  "co": 3.5,
  "movement": "WALKING",
  "fall": false,
  "immobile": false,
  "sos": false,
  "risk_level": "CRITICAL",
  "battery": 85
}
```

Backend có thể tạo Event:

```json
{
  "event_type": "TEMPERATURE_HIGH",
  "severity": "CRITICAL"
}
```

## Chức năng hoàn thành

* Tích hợp Rule-based Safety Engine vào Backend.
* Đánh giá Telemetry sau khi Pydantic validation thành công.
* Backend tự quyết định `risk_level`.
* Không tin `risk_level` từ Simulator.
* Xác định Safety Reasons.
* Tự động tạo Safety Event.
* Xác định Event Type từ Safety Reason.
* Xác định Event Severity từ Risk Level.
* Lưu Telemetry đã đánh giá vào PostgreSQL.
* Lưu Safety Event vào PostgreSQL.
* Không tạo Event đối với trạng thái `NORMAL`.
* Bỏ qua Event do Simulator gửi để tránh tạo Event trùng.

## Không nằm trong Milestone 6

Các chức năng sau chưa được triển khai:

* AI / Machine Learning.
* Camera / Computer Vision.
* Alert Notification thực tế.
* WebSocket Realtime.
* Dashboard nghiệp vụ.
* Hardware Integration.

---

# Milestone 7 – Scenario Engine & Safety Verification

Milestone 7 bổ sung **Scenario Engine** cho Python Simulator nhằm tạo ra nhiều tình huống hoạt động khác nhau của Smart Rescue Helmet.

Mục tiêu của Milestone 7 là kiểm chứng toàn bộ pipeline từ điều kiện của thiết bị đến kết quả đánh giá của Backend.

Scenario chỉ có nhiệm vụ tạo dữ liệu cảm biến và trạng thái thiết bị. Scenario **không quyết định `risk_level` và không tạo Event**.

## Software Architecture

```text
Scenario
   │
   ▼
Sensor / State Data
   │
   ▼
PayloadFactory
   │
   ▼
MQTT
   │
   ▼
Backend
   │
   ▼
SafetyEngine
   │
   ├── Risk Level
   │
   └── Safety Reasons
          │
          ▼
       Event
          │
          ▼
     PostgreSQL
```

## Các Scenario

Simulator hiện hỗ trợ các Scenario:

| Scenario                  | Điều kiện mô phỏng               | Risk mong đợi |
| ------------------------- | -------------------------------- | ------------- |
| `NormalScenario`          | Hoạt động bình thường            | `NORMAL`      |
| `TemperatureHighScenario` | Temperature = 75°C               | `CRITICAL`    |
| `COHighScenario`          | CO = 150                         | `CRITICAL`    |
| `FallScenario`            | `fall = true`                    | `CRITICAL`    |
| `FallImmobileScenario`    | `fall = true`, `immobile = true` | `CRITICAL`    |
| `SOSScenario`             | `sos = true`                     | `CRITICAL`    |
| `LowBatteryScenario`      | Battery = 10%                    | `WARNING`     |

## Nguyên tắc thiết kế Scenario

Scenario chỉ tạo **điều kiện đầu vào**.

Ví dụ:

```python
return {
    "temperature": 75,
    "co": self.co.read(),
    "movement": "WALKING",
    "fall": False,
    "immobile": False,
    "sos": False,
}
```

Scenario không chứa:

```python
"risk_level": "CRITICAL"
```

Việc xác định Risk được thực hiện bởi Backend:

```text
Scenario
   ↓
temperature = 75
   ↓
MQTT
   ↓
SafetyEngine
   ↓
temperature >= 60
   ↓
CRITICAL_TEMPERATURE
   ↓
RiskLevel.CRITICAL
```

Thiết kế này đảm bảo Simulator không can thiệp vào logic nghiệp vụ của Backend.

## Safety Verification

Các Scenario được chạy lần lượt để kiểm tra kết quả thực tế của hệ thống.

### NORMAL

Điều kiện:

```text
temperature < 50
co < 50
battery > 20
fall = false
immobile = false
sos = false
```

Kết quả:

```text
Risk Level = NORMAL
Event = None
```

### HIGH TEMPERATURE

Điều kiện:

```text
temperature = 75°C
```

Kết quả:

```text
Risk Level = CRITICAL
Event Type = TEMPERATURE_HIGH
Severity = CRITICAL
```

### HIGH CO

Điều kiện:

```text
co = 150
```

Kết quả:

```text
Risk Level = CRITICAL
Event Type = CO_HIGH
Severity = CRITICAL
```

### FALL

Điều kiện:

```text
fall = true
immobile = false
```

Kết quả:

```text
Risk Level = CRITICAL
Event Type = FALL_DETECTED
Severity = CRITICAL
```

### FALL + IMMOBILE

Điều kiện:

```text
fall = true
immobile = true
```

Kết quả:

```text
Risk Level = CRITICAL
Event Type = FALL_DETECTED
Severity = CRITICAL
```

### SOS

Điều kiện:

```text
sos = true
```

Kết quả:

```text
Risk Level = CRITICAL
Event Type = SOS_PRESSED
Severity = CRITICAL
```

### LOW BATTERY

Điều kiện:

```text
battery = 10%
```

Kết quả:

```text
Risk Level = WARNING
Event Type = LOW_BATTERY
Severity = WARNING
```

## Verification Result

Toàn bộ 7 Scenario đã được kiểm thử:

| Scenario         | Risk Level | Event              | Verification |
| ---------------- | ---------- | ------------------ | ------------ |
| NORMAL           | `NORMAL`   | Không có           | ✅ PASS       |
| HIGH TEMPERATURE | `CRITICAL` | `TEMPERATURE_HIGH` | ✅ PASS       |
| HIGH CO          | `CRITICAL` | `CO_HIGH`          | ✅ PASS       |
| FALL             | `CRITICAL` | `FALL_DETECTED`    | ✅ PASS       |
| FALL + IMMOBILE  | `CRITICAL` | `FALL_DETECTED`    | ✅ PASS       |
| SOS              | `CRITICAL` | `SOS_PRESSED`      | ✅ PASS       |
| LOW BATTERY      | `WARNING`  | `LOW_BATTERY`      | ✅ PASS       |

## Data Flow hoàn chỉnh

```text
                    Python Simulator
                           │
                           ▼
                      Scenario
                           │
                           ▼
                    PayloadFactory
                           │
                           ▼
                    MQTT Publisher
                           │
                           ▼
                   Mosquitto Broker
                           │
                           ▼
                 FastAPI MQTT Subscriber
                           │
                           ▼
                  Pydantic Validation
                           │
                           ▼
                     Safety Engine
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                Risk Level     Reasons
                    │             │
                    └──────┬──────┘
                           ▼
                    Event Creation
                           │
                           ▼
                      PostgreSQL
```

## Chức năng hoàn thành

* Xây dựng Scenario Engine cho Simulator.
* Hỗ trợ Scenario NORMAL.
* Hỗ trợ Scenario HIGH TEMPERATURE.
* Hỗ trợ Scenario HIGH CO.
* Hỗ trợ Scenario FALL.
* Hỗ trợ Scenario FALL + IMMOBILE.
* Hỗ trợ Scenario SOS.
* Hỗ trợ Scenario LOW BATTERY.
* Tách Scenario khỏi Safety Engine.
* Scenario chỉ tạo điều kiện dữ liệu.
* Backend Safety Engine là nguồn quyết định Risk Level.
* Kiểm thử toàn bộ pipeline MQTT → Backend → Safety Engine → PostgreSQL.
* Xác minh Risk Level của từng Scenario.
* Xác minh Event Type và Severity của các tình huống nguy hiểm.
* Xác minh NORMAL không tạo Safety Event.

## Không nằm trong Milestone 7

Các chức năng sau chưa được triển khai trong milestone này:

* AI / Machine Learning.
* Camera / Computer Vision.
* Hardware ESP32-S3 thật.
* Alert Notification thực tế.
* WebSocket Realtime.
* Dashboard nghiệp vụ hoàn chỉnh.
* Location / GPS.
* Navigation.
* Phân tích dữ liệu nâng cao.

---

## Milestone hiện tại

**Milestone 7 — Scenario Engine & Safety Verification**

* Rule-based Safety Engine đã hoạt động.
* Backend tự quyết định Risk Level.
* Safety Event được tạo từ Safety Result.
* Python Simulator hỗ trợ 7 Scenario.
* Đã kiểm thử NORMAL, HIGH TEMPERATURE, HIGH CO, FALL, FALL + IMMOBILE, SOS và LOW BATTERY.
* Các Scenario đều cho kết quả đúng theo Safety Rules.
* PostgreSQL lưu Telemetry và Safety Event.
* Simulator không quyết định Risk Level nghiệp vụ.
* Simulator không tự tạo Safety Event.
