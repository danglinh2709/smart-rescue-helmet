# Shared MQTT contract

Thư mục này chứa interface dùng chung giữa publisher của helmet và Backend.

Publisher có thể là:

- Python Simulator trong giai đoạn software-first.
- ESP32-S3 trong giai đoạn hardware integration.

Cả hai publisher phải tuân thủ cùng MQTT topic, JSON payload, enum, schema version, timestamp và device ID. Khi tích hợp phần cứng, chỉ publisher được thay thế; Backend không đổi contract và không phân nhánh business logic theo `source`.

## Source of truth

Pydantic models trong `backend/app/schemas/` là source of truth. Các file trong `shared/contracts/` được generate từ model bằng:

```powershell
cd backend
python -m scripts.export_json_schemas
```

Không sửa trực tiếp JSON Schema đã generate. Mọi thay đổi contract phải bắt đầu từ Pydantic model, có test, rồi export lại artifact.

## Common message envelope

Mọi message có bốn trường chung:

| Field | Rule |
|---|---|
| `schema_version` | Bắt buộc và bằng `1.0` trong contract hiện tại |
| `device_id` | 3–32 ký tự; bắt đầu bằng `A-Z`; các ký tự còn lại là `A-Z`, `0-9`, `_`, `-` |
| `timestamp` | ISO-8601/RFC 3339 và bắt buộc có timezone |
| `source` | `SIMULATOR` hoặc `HARDWARE`; chỉ dùng cho tracking/debugging |

Ví dụ device ID hợp lệ: `FF01`, `FF02`, `HELMET-04`, `RESCUE_TEAM_3`.

## Contract artifacts

- `mqtt_topics.md`: topic patterns và trách nhiệm publisher/subscriber.
- `enums.md`: wire values của các enum dùng chung.
- `contracts/telemetry.schema.json`: telemetry định kỳ.
- `contracts/event.schema.json`: sự kiện an toàn/bất thường.
- `contracts/status.schema.json`: trạng thái logic hiện tại.
- `contracts/health.schema.json`: tình trạng thiết bị, kết nối và sensor.

Milestone 2 chỉ định nghĩa và kiểm thử contract. Không có MQTT publisher/subscriber, Simulator runtime, Safety Engine, database nghiệp vụ, WebSocket hoặc Dashboard nghiệp vụ.
