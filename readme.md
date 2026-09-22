## Milestone 4 – MQTT → Backend
MQTT Subscriber

FastAPI Backend được mở rộng để hoạt động như một MQTT Subscriber. Backend kết nối tới Eclipse Mosquitto, subscribe các MQTT topics đã định nghĩa trong Shared Contract và tiếp nhận dữ liệu được publish từ Python Simulator.

Mỗi MQTT message sau khi nhận sẽ được parse từ JSON và validate bằng các Pydantic models dùng chung. Nếu payload hợp lệ, Backend cập nhật trạng thái hiện tại của thiết bị trong runtime để chuẩn bị cho các bước lưu trữ, phân tích và realtime ở các milestone tiếp theo.

Milestone này chỉ tập trung xây dựng pipeline từ MQTT đến Backend. Database nghiệp vụ, Safety Engine, WebSocket và Dashboard vẫn chưa được triển khai.


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
JSON Parsing
       │
       ▼
Pydantic Validation
       │
       ▼
Device Runtime State
```


## MQTT Message Flow
```text
Python Simulator
        │
 Publish MQTT Message
        │
        ▼
Mosquitto Broker
        │
        ▼
FastAPI Subscriber
        │
        ▼
Parse JSON
        │
        ▼
Validate bằng Pydantic
        │
        ▼
Update Runtime Device State
```

## MQTT Topics

Backend subscribe các topic sau:

| Topic | Description |
| --- | --- |
| `helmet/+/telemetry` | Sensor telemetry |
| `helmet/+/status` | Device status |
| `helmet/+/health` | Device health |
| `helmet/+/event` | Device event |

## Milestone Scope
Hoàn thành trong Milestone 4:
- FastAPI kết nối tới Eclipse Mosquitto.
- Subscribe các MQTT topics theo Shared Contract.
- Nhận và parse MQTT payload dạng JSON.
- Validate payload bằng Pydantic models.
- Cập nhật trạng thái thiết bị trong runtime.
- Ghi log khi nhận thành công hoặc validation thất bại.
- Hỗ trợ tự động reconnect tới MQTT Broker.
## Out of Scope

Các chức năng sau không nằm trong Milestone 4:

- Lưu dữ liệu vào PostgreSQL.
- Lưu lịch sử Telemetry, Event và Health.
- Rule-based Safety Engine.
- Realtime WebSocket.
- Dashboard nghiệp vụ.
- Hardware Integration.
## Milestone hiện tại

Milestone 4 — MQTT Subscriber + Backend Runtime

- FastAPI hoạt động như MQTT Subscriber.
- Subscribe telemetry, status, health và event topics.
- Parse JSON payload từ MQTT.
- Validate bằng Pydantic v2.
- Cập nhật trạng thái thiết bị trong runtime.
- Ghi log khi nhận hoặc khi payload không hợp lệ.
- Tự động reconnect khi MQTT Broker mất kết nối.

Chưa có:

- Database Persistence.
- Safety Engine.
- WebSocket Realtime.
- Dashboard nghiệp vụ.
- Hardware Integration.

##
##
## Milestone 5 – Database & History
Database Persistence

FastAPI Backend được mở rộng để lưu dữ liệu nhận từ MQTT vào PostgreSQL. Sau khi một MQTT message được validate thành công, Backend sẽ ghi dữ liệu vào các bảng tương ứng để phục vụ việc truy vấn lịch sử và phân tích sau này.

Milestone này xây dựng lớp Database Persistence, bao gồm quản lý thiết bị, lưu lịch sử telemetry, event và health. Dữ liệu được lưu theo thời gian (timestamp) nhằm hỗ trợ theo dõi trạng thái thiết bị và phục vụ các milestone về Safety Engine, Dashboard và Analytics.

Milestone này chưa triển khai Rule-based Safety Engine, WebSocket Realtime và Dashboard nghiệp vụ.

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
```
## Database Processing Flow
```text
Python Simulator
        │
 Publish MQTT Message
        │
        ▼
Mosquitto Broker
        │
        ▼
FastAPI Subscriber
        │
        ▼
Parse JSON
        │
        ▼
Validate bằng Pydantic
        │
        ▼
Insert / Update Database
        │
        ▼
Historical Data
```

## Database Tables
| Topic | Description |
| --- | --- |
|Devices | Lưu thông tin thiết bị và trạng thái hiện tại |
| Telemetry | Lưu lịch sử dữ liệu cảm biến |
| Events | Lưu các sự kiện phát sinh từ thiết bị|
| Health |Lưu lịch sử trạng thái sức khỏe thiết bị|


## Milestone Scope
Hoàn thành trong Milestone 5:
- Kết nối FastAPI với PostgreSQL.
- Thiết kế các bảng Devices, Telemetry, Events và Health.
- Lưu dữ liệu Telemetry vào Database.
- Lưu dữ liệu Status của thiết bị.
- Lưu dữ liệu Health.
- Lưu Event khi thiết bị publish.
- Cập nhật thông tin thiết bị hiện tại.
- Hỗ trợ truy vấn lịch sử dữ liệu theo thiết bị và thời gian.

## Out of Scope
Các chức năng sau không nằm trong Milestone 5:
- Rule-based Safety Engine.
- Risk Assessment.
- Alert Generation.
- WebSocket Realtime.
- Dashboard nghiệp vụ.
- Hardware Integration.

## Milestone hiện tại
Milestone 5 — Database Persistence & History
- FastAPI lưu dữ liệu vào PostgreSQL.
- Quản lý thông tin thiết bị (Devices).
- Lưu lịch sử Telemetry.
- Lưu lịch sử Events.
- Lưu lịch sử Health.
- Cập nhật trạng thái thiết bị.
- Hỗ trợ truy vấn dữ liệu lịch sử.

Chưa có:

- Safety Engine.
- Risk Detection.
- WebSocket Realtime.
- Dashboard nghiệp vụ.
- Hardware Integration.

##
##
## Milestone 6 – Safety Engine
Rule-based Risk Engine

FastAPI Backend được mở rộng với Safety Engine để đánh giá mức độ an toàn của thiết bị dựa trên các dữ liệu Telemetry, Event và Health. Safety Engine sử dụng các luật (Rule-based) được định nghĩa sẵn để phân loại trạng thái của thiết bị thành ba mức:

- NORMAL
- WARNING
- CRITICAL

Các luật đánh giá được áp dụng cho các thông số như nhiệt độ, nồng độ khí CO, sự kiện ngã (Fall Detection), trạng thái bất động (Immobile) và nút khẩn cấp (SOS).

Milestone này chỉ tập trung vào đánh giá rủi ro và cập nhật mức độ cảnh báo. Việc hiển thị cảnh báo theo thời gian thực trên Dashboard sẽ được triển khai ở các milestone tiếp theo.

## Software Architecture
```text
Python Simulator
        │
        ▼
MQTT Broker (Mosquitto)
        │
        ▼
FastAPI Backend
        │
        ▼
Safety Engine
        │
        ▼
Risk Assessment
```
## Safety Processing Flow
```text
MQTT Message
        │
        ▼
Parse JSON
        │
        ▼
Validate bằng Pydantic
        │
        ▼
Read Device Data
        │
        ▼
Safety Rule Evaluation
        │
        ▼
Risk Level
(NORMAL / WARNING / CRITICAL)
``` 

## Safety Rules

Safety Engine đánh giá dựa trên các điều kiện sau:

| Rule | Mô tả |
| --- | --- |
|Temperature | Kiểm tra nhiệt độ vượt ngưỡng |
|CO | Kiểm tra nồng độ khí CO |
|Fall | Detection	Phát hiện người dùng bị ngã |
|Immobile | Phát hiện bất động trong thời gian quy định 
|SOS | Button	Người dùng nhấn nút khẩn cấp |

## Risk Levels
| Level | Ý nghĩa |
| --- | --- |
|NORMAL | Thiết bị hoạt động bình thường |
|WARNING | Có dấu hiệu bất thường, cần theo dõi |
|CRITICAL | Nguy hiểm, cần xử lý ngay |

## Milestone Scope
Hoàn thành trong Milestone 6:
- Xây dựng Rule-based Safety Engine.
- Đánh giá dữ liệu Telemetry và Event.
- Xác định mức độ rủi ro của thiết bị.
- Phân loại NORMAL, WARNING và CRITICAL.
- Cập nhật trạng thái an toàn của thiết bị.
- Ghi log kết quả đánh giá.

## Out of Scope
Các chức năng sau không nằm trong Milestone 6:
- Scenario Engine.
- Alert Notification.
- WebSocket Realtime.
- Dashboard nghiệp vụ.
- Hardware Integration.
## Milestone hiện tại
Milestone 6 — Rule-based Safety Engine
- Đánh giá dữ liệu cảm biến theo các luật định sẵn.
- Kiểm tra nhiệt độ.
- Kiểm tra nồng độ khí CO.
- Phát hiện Fall Detection.
- Phát hiện Immobile.
- Phát hiện SOS Button.
- Phân loại NORMAL, WARNING và CRITICAL.
- Cập nhật trạng thái an toàn của thiết bị.
- Ghi log kết quả đánh giá.

Chưa có:

- Scenario Engine.
- Realtime Alert.
- WebSocket.
- Dashboard nghiệp vụ.
- Hardware Integration.


##
##
## Milestone 7 – Scenario Engine
Scenario-based Event Processing

FastAPI Backend được mở rộng với Scenario Engine nhằm phát hiện và xử lý các tình huống thực tế dựa trên dữ liệu từ Safety Engine. Thay vì chỉ đánh giá từng điều kiện riêng lẻ, Scenario Engine kết hợp nhiều thông tin Telemetry, Event và Health để xác định các kịch bản hoạt động của thiết bị.

Mỗi kịch bản được ánh xạ tới một loại sự kiện (Scenario) nhằm chuẩn bị cho việc phát cảnh báo, hiển thị Dashboard và hỗ trợ công tác cứu hộ trong các milestone tiếp theo.

Milestone này tập trung vào xác định Scenario và tạo Event Runtime. Chức năng gửi cảnh báo realtime và Dashboard sẽ được triển khai ở các milestone sau.

## Software Architecture 
```text
Python Simulator
        │
        ▼
MQTT Broker (Mosquitto)
        │
        ▼
FastAPI Backend
        │
        ▼
Safety Engine
        │
        ▼
Scenario Engine
        │
        ▼
Scenario Event
```

## Scenario Processing Flow
```text
Telemetry / Event / Health
            │
            ▼
Safety Engine
            │
            ▼
Evaluate Scenario Rules
            │
            ▼
Generate Scenario Event
            │
            ▼
Update Device Scenario
```

## Supported Scenarios
|Scenario | Description |
| --- | --- |
|NORMAL | Thiết bị hoạt động bình thường |
|HIGH_TEMP | Nhiệt độ vượt ngưỡng |
|HIGH_CO | Nồng độ khí CO vượt ngưỡng |
|FALL | Phát hiện người dùng bị ngã |
|FALL_IMMOBILE | Người dùng bị ngã và bất động |
|SOS | Người dùng nhấn nút khẩn cấp |
|OW_BATTERY | Pin thiết bị ở mức thấp |

## Milestone Scope
Hoàn thành trong Milestone 7:
- Xây dựng Scenario Engine.
- Định nghĩa các Scenario Rules.
- Phát hiện HIGH_TEMP.
- Phát hiện HIGH_CO.
- Phát hiện FALL.
- Phát hiện FALL_IMMOBILE.
- Phát hiện SOS.
- Phát hiện LOW_BATTERY.
- Sinh Scenario Event.
- Cập nhật Scenario hiện tại của thiết bị.

## Out of Scope
Các chức năng sau không nằm trong Milestone 7:
- WebSocket Realtime.
- Dashboard nghiệp vụ.
- Push Notification.
- Hardware Integration.

## Milestone hiện tại
Milestone 7 — Scenario Engine
- Xây dựng Scenario Engine.
- Định nghĩa Scenario Rules.
- Phát hiện HIGH_TEMP.
- Phát hiện HIGH_CO.
- Phát hiện FALL.
- Phát hiện FALL_IMMOBILE.
- Phát hiện SOS.
- Phát hiện LOW_BATTERY.
- Sinh Scenario Event.
- Cập nhật Scenario hiện tại của thiết bị.

Chưa có:

- WebSocket Realtime.
- Dashboard nghiệp vụ.
- Push Notification.
- Hardware Integration.