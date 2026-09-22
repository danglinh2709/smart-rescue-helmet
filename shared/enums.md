# Shared enum values

Các giá trị dưới đây được truyền nguyên dạng trên wire và phân biệt chữ hoa/chữ thường.

## RiskLevel

- `NORMAL`
- `WARNING`
- `CRITICAL`

## DeviceStatus

- `ONLINE`
- `OFFLINE`

## ConnectionStatus

- `CONNECTED`
- `DISCONNECTED`

## MovementState

- `UNKNOWN`
- `STATIONARY`
- `WALKING`
- `RUNNING`
- `CRAWLING`
- `UNUSUAL_MOVEMENT`
- `FALL`
- `IMMOBILE`

## EventType

- `TEMPERATURE_HIGH`
- `CO_HIGH`
- `UNUSUAL_MOVEMENT`
- `FALL_DETECTED`
- `IMMOBILE`
- `SOS_PRESSED`
- `LOW_BATTERY`
- `DEVICE_OFFLINE`
- `MQTT_DISCONNECTED`
- `MQTT_RECONNECTED`

## EventSeverity

- `INFO`
- `WARNING`
- `CRITICAL`

## DataSource

- `SIMULATOR`
- `HARDWARE`

`source` chỉ phục vụ debugging/tracking. Backend không được dùng giá trị này để tạo hai nhánh business logic.

## SensorStatus

- `OK`
- `ERROR`
- `UNAVAILABLE`
