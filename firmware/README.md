# Firmware ESP32-S3 — Smart Rescue Helmet

Firmware này là nền tảng phần cứng cho ESP32-S3. Nó giữ nguyên MQTT contract
đang dùng bởi Python Simulator: `helmet/{device_id}/telemetry`, `status`,
`health` và `event`; payload luôn có `schema_version: "1.0"` và
`source: "HARDWARE"`.

## Chuẩn bị

- ESP-IDF 6.1 hoặc phiên bản ESP-IDF tương thích.
- ESP32-S3-DevKitC-1.
- Nguồn bench 5 V / 2 A và cáp USB dữ liệu.
- Đồng hồ đo điện áp trước khi nối buzzer hoặc vibration motor.

Không lưu Wi-Fi hay MQTT password trong source. Thiết lập bằng:

```powershell
idf.py set-target esp32s3
idf.py menuconfig
idf.py build
idf.py -p COMx flash monitor
```

## Sơ đồ chân prototype

| Chức năng | GPIO |
| --- | ---: |
| I2C SDA / SCL | 8 / 9 |
| DS18B20 | 4 |
| SOS (pull-up, nhấn xuống GND) | 5 |
| LED xanh / vàng / đỏ | 6 / 7 / 15 |
| Buzzer / vibration MOSFET | 16 / 17 |
| Battery divider ADC | 1 |

MQ-7 module dùng 5 V. **Không nối analog MQ-7 trực tiếp vào ESP32**; dùng
ADS1115 chạy 3.3 V hoặc mạch chia áp/bảo vệ phù hợp. Buzzer và motor phải qua
transistor/MOSFET; motor cần diode flyback.

## Kiểm tra bench an toàn

1. Tắt nguồn, kiểm tra GND chung và điện áp bằng multimeter.
2. Chỉ nối I2C và flash firmware trước.
3. Theo dõi serial log rồi dùng `mosquitto_sub -t "helmet/#" -v` để xác minh
   dữ liệu MQTT khi phần publish đã được cấu hình.
4. Chỉ sau đó mới nối buzzer và motor qua mạch driver.

Prototype này không phải thiết bị cứu hộ đã được chứng nhận.
