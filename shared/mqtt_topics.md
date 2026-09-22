# MQTT topic contract

Mọi topic nằm dưới namespace `helmet/{device_id}`. `{device_id}` phải tuân thủ format mô tả trong `shared/README.md`; ký tự `/`, `+`, `#` và chữ thường không hợp lệ.

| Topic Pattern | Publisher | Subscriber | Purpose |
|---|---|---|---|
| `helmet/{device_id}/telemetry` | Simulator / ESP32-S3 | Backend | Periodic sensor data |
| `helmet/{device_id}/event` | Simulator / ESP32-S3 | Backend | Safety or abnormal event |
| `helmet/{device_id}/status` | Simulator / ESP32-S3 | Backend | Current logical helmet state |
| `helmet/{device_id}/health` | Simulator / ESP32-S3 | Backend | Device, connection, and sensor health |

Ví dụ cho thiết bị `FF01`:

```text
helmet/FF01/telemetry
helmet/FF01/event
helmet/FF01/status
helmet/FF01/health
```

## Message purposes

- `telemetry`: dữ liệu sensor gửi định kỳ, kèm movement/state, risk level và thông tin kết nối tại thời điểm đo.
- `event`: sự kiện bất thường hoặc an toàn, có top-level ổn định và `data` linh hoạt theo ngữ cảnh.
- `status`: trạng thái logic hiện tại của helmet.
- `health`: battery, uptime, kết nối Wi-Fi/MQTT và tình trạng từng sensor.

File này chỉ định nghĩa naming contract. Milestone 2 không tạo kết nối, publish, subscribe, QoS policy hoặc retained-message policy.
