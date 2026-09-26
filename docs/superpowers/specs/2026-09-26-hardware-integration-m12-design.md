# Thiết kế Tích hợp Phần cứng M12 Smart Rescue Helmet V1

## Mục tiêu và phạm vi

Thiết kế này thay Python Simulator bằng publisher phần cứng ESP32-S3 mà không thay đổi Backend, PostgreSQL, WebSocket, React Dashboard hoặc MQTT wire contract. Thiết kế hiện thực hóa mục tiêu chức năng F01 đến F20 của `Smart_Rescue_Helmet_V1_Dac_ta_chuc_nang.docx`, bắt đầu bằng prototype trên bàn thử nghiệm rồi đến pilot đeo được.

Đây là prototype phục vụ học tập. Nó không phải thiết bị cứu hộ chữa cháy được chứng nhận và không được dùng để đưa ra quyết định an toàn tính mạng. MQ-7 chỉ phù hợp cho demo và hiệu chuẩn, không phải cảm biến bảo vệ CO được chứng nhận.

## Quyết định kiến trúc

Đặc tả Word là chuẩn về chức năng. Shared MQTT contract hiện có vẫn là chuẩn truyền dữ liệu:

```text
DS18B20 / MQ-7 / MPU6050 / SOS / pin
                    |
                    v
             Firmware ESP32-S3
              |             |
              |             +--> Local Safety Engine --> LED / buzzer / vibration
              v
Wi-Fi + MQTT telemetry/status/health (source=HARDWARE)
              |
              v
Mosquitto --> FastAPI validation --> Backend Safety Engine --> PostgreSQL
                                               |                 |
                                               +--> WebSocket --> Dashboard
```

Thiết bị chỉ publish các topic đã được chốt:

- `helmet/{device_id}/telemetry`
- `helmet/{device_id}/status`
- `helmet/{device_id}/health`
- `helmet/{device_id}/event` vẫn được giữ lại trong shared contract.

Temperature, CO, IMU và SOS là các trường trong cùng một telemetry snapshot nguyên tử; không bổ sung các topic cảm biến riêng lẻ kiểu cũ trong tài liệu Word. Backend vẫn là nơi có thẩm quyền tạo event được lưu và hiển thị trên Dashboard để thiết bị không thể tạo alert trùng hoặc chưa được validation. ESP32 vẫn tự đánh giá cùng trạng thái an toàn tại chỗ để điều khiển actuator ngay lập tức.

## Danh sách linh kiện cho hardware prototype

### Bắt buộc cho prototype trên bàn thử nghiệm

| Linh kiện | Số lượng | Yêu cầu |
|---|---:|---|
| ESP32-S3-DevKitC-1 N8R8 | 1 | Board chính hãng, cáp USB có data |
| MPU6050 / GY-521 | 1 | Mạch breakout IMU I2C |
| DS18B20 waterproof probe | 1 | Chế độ ba dây, điện trở pull-up 4.7 kOhm |
| MQ-7 module | 1 | Có analog output, cấp nguồn 5 V |
| ADS1115 module | 1 | ADC I2C 16-bit cho analog output MQ-7 đã được điều hòa điện áp |
| Nút SOS | 1 | Momentary, thường hở; ưu tiên chống nước |
| LED | 3 | Đỏ, vàng, xanh; mỗi LED có điện trở 220-330 Ohm |
| Active buzzer | 1 | Loại 3.3 V hoặc được điều khiển transistor đúng cách |
| Coin vibration motor | 1 | Loại 3 V |
| N-channel MOSFET | 2 | Mỗi motor và buzzer một mạch low-side nếu cần |
| Flyback diode | 1 | Schottky diode mắc song song với vibration motor |
| Breadboard và dây Dupont | 1 bộ | Chỉ dùng để lắp thử trên bàn |
| Nguồn USB | 1 | Ổn định, tối thiểu 5 V / 2 A |
| Multimeter | 1 | Bắt buộc để đo điện áp và kiểm tra thông mạch |

### Phần bổ sung cho pilot có thể đeo, sau khi bench prototype đạt yêu cầu

- Pin LiPo 3.7 V có bảo vệ, 2000-3000 mAh.
- Mạch sạc USB-C có power-path/load-sharing thực sự.
- Mạch boost 5 V phù hợp tải và rail 3.3 V được điều áp ổn định.
- Cầu chì hoặc polyfuse reset được, công tắc nguồn, đầu JST và dây silicone.
- Vỏ/mounting, chống gãy dây và nút SOS ngoài đạt yêu cầu môi trường dự kiến.

Không dùng module TP4056 đơn thuần làm mạch vừa sạc vừa cấp tải. Không gắn MQ-7 heater, pin hoặc breadboard/dây điện hở trực tiếp lên mũ.

## Đi dây trên bàn thử nghiệm và phân bổ GPIO

Phân bổ này dành cho ESP32-S3-DevKitC-1, tránh GPIO0, chân USB GPIO19/GPIO20, UART GPIO43/GPIO44 và chân RGB LED onboard phụ thuộc phiên bản board.

| Chức năng | Chân ESP32-S3 | Lưu ý điện |
|---|---:|---|
| I2C SDA, MPU6050 và ADS1115 | GPIO8 | Bus I2C 3.3 V |
| I2C SCL, MPU6050 và ADS1115 | GPIO9 | Bus I2C 3.3 V |
| Data DS18B20 | GPIO4 | Pull-up 4.7 kOhm đến 3.3 V |
| Input SOS | GPIO5 | Internal pull-up, nút nối GND, có debounce |
| LED xanh | GPIO6 | Có điện trở nối tiếp |
| LED vàng | GPIO7 | Có điện trở nối tiếp |
| LED đỏ | GPIO15 | Có điện trở nối tiếp |
| Driver buzzer | GPIO16 | Dùng MOSFET nếu dòng tải yêu cầu |
| Driver vibration motor | GPIO17 | MOSFET low-side + flyback diode |
| ADC chia áp pin | GPIO1 | Chia áp đã hiệu chuẩn, tuyệt đối không quá 3.3 V |

Tất cả module phải dùng chung GND. MQ-7 module dùng 5 V. Analog output của nó phải được điều hòa để luôn nằm trong input range của ADS1115 tham chiếu nguồn ADS1115 3.3 V. Không bao giờ nối trực tiếp vào GPIO ESP32 hoặc ADC 3.3 V. Curve hiệu chuẩn, heater cycle, thời gian warm-up và tỉ lệ chia áp MQ-7 phải được đo và ghi nhận trước khi báo giá trị CO theo ppm.

## Kiến trúc firmware

Firmware nằm trong `firmware/`, dùng ESP-IDF với CMake. Firmware dùng FreeRTOS task và `esp-mqtt` của ESP-IDF; credential nằm trong NVS hoặc development configuration lúc build, không bao giờ commit vào source code.

| Module | Trách nhiệm |
|---|---|
| `config` | Device ID, cấu hình Wi-Fi/MQTT, interval và safety threshold |
| `drivers` | DS18B20, MPU6050, ADS1115/MQ-7, SOS, pin và actuator |
| `sensing` | Tạo sensor snapshot có timestamp và cờ hợp lệ |
| `detection` | Suy ra fall, immobility và movement state từ mẫu IMU |
| `safety` | Đánh giá local risk thuần túy từ sensor snapshot |
| `actuators` | Áp dụng an toàn trạng thái xanh/tắt/tắt, vàng/tắt/tắt, đỏ/bật/bật |
| `network` | Wi-Fi, đồng bộ NTP, kết nối MQTT và xử lý reconnect |
| `contract` | Serialize JSON `1.0` strict cho telemetry, status và health |
| `main` | Khởi động task, watchdog-safe loop và shutdown sạch |

Sampling và publishing độc lập. IMU sample ở 50 Hz, sensor snapshot thông thường ở 1 Hz, telemetry mỗi 1 giây, status mỗi 2 giây và health mỗi 5 giây. Một sensor sample hợp lệ phải cập nhật local safety trước bất kỳ thao tác MQTT nào.

## Local safety và fail-safe

Các rule local ban đầu phản chiếu backend threshold hiện tại:

| Điều kiện | Risk | Kết quả local actuator |
|---|---|---|
| Bình thường | NORMAL | xanh, buzzer tắt, vibration tắt |
| Temperature 50-59.99 C, CO 50-99.99, pin <=20% | WARNING | vàng, buzzer tắt, vibration tắt |
| Temperature >=60 C, CO >=100, SOS, fall | CRITICAL | đỏ, buzzer bật, vibration bật |

Fall detection là rule IMU đã hiệu chuẩn, không phải một ngưỡng gia tốc thô: candidate free-fall/impact, thay đổi orientation và một khoảng thời gian xác nhận ngắn. Implementation đầu tiên phải đưa các threshold vào cấu hình và có IMU fixture đã ghi lại.

Immobility được triển khai bằng khoảng thời gian có low motion có thể cấu hình. Để khớp đặc tả V1, một immobility event được báo là `IMMOBILE`; risk của nó phải được kiểm thử rõ ràng: WARNING khi đứng một mình và CRITICAL khi kết hợp fall. Điều này thay đổi quyết định prototype hiện tại, nơi immobility đơn lẻ vẫn là NORMAL, nên phải được triển khai nhất quán cho backend và firmware trong cùng một thay đổi đã lập kế hoạch.

Khi Wi-Fi, MQTT, NTP hoặc backend không khả dụng, sensing, local detection và actuator vẫn hoạt động. MQTT reconnect bằng bounded exponential backoff. V1 không cần offline telemetry queue; trạng thái hợp lệ mới nhất sẽ được publish sau khi kết nối lại.

## Triển khai wire contract

Mọi message gửi đi dùng:

- `schema_version: "1.0"`
- device ID đã provision như `FF01` hoặc `HELMET-04`
- `source: "HARDWARE"`
- timestamp RFC 3339 / ISO-8601 có timezone, đồng bộ bằng NTP
- giá trị enum strict từ `shared/enums.md`

Trước khi NTP đồng bộ, firmware không được publish wall-clock timestamp giả. Nó đánh dấu health nội bộ là unavailable và chờ đồng bộ thời gian; sau startup grace period có cấu hình, firmware chỉ publish sensor field khi có timestamp tuân thủ contract.

Sensor failure được biểu diễn bằng `temperature: null` hoặc `co: null` theo JSON schema và bằng `SensorStatus.ERROR` hoặc `SensorStatus.UNAVAILABLE` trong health. IMU field là bắt buộc; MPU6050 lỗi sẽ ngăn telemetry payload được publish và xuất hiện trong health ngay khi đã có timestamp hợp lệ.

## Bảo mật và provisioning

Bench integration dùng anonymous broker local hiện tại, chỉ trên development network cô lập. Wearable pilot bắt buộc có:

- Wi-Fi và MQTT credential cho từng device;
- MQTT authentication và ACL giới hạn từng device trong namespace `helmet/{device_id}/#` của nó;
- TLS cho MQTT và WSS/HTTPS cho dashboard access;
- credential nằm ngoài Git; và
- factory/provisioning procedure có tài liệu cho device ID và Wi-Fi setup.

## Verification và acceptance

### Unit test và bench test

1. Kiểm tra độc lập từng thiết bị I2C và 1-Wire với số đo thực.
2. Kiểm tra SOS debounce, LED state, buzzer output và motor MOSFET output bằng multimeter trước khi kết nối wearable.
3. Validate telemetry/status/health tạo ra với shared JSON schema.
4. Test normal, high temperature, high CO, SOS, fall, immobility, low battery, sensor failure, Wi-Fi loss và MQTT loss.
5. Xác nhận local actuator critical hoạt động khi MQTT bị tắt.

### Tiêu chí tích hợp

1. ESP32 publish message đúng contract đến Mosquitto broker hiện có.
2. Backend nhận message mà không phải thay đổi architecture, hiển thị `source=HARDWARE`.
3. PostgreSQL lưu telemetry, health và canonical event do backend tạo.
4. WebSocket và dashboard hiển thị cùng device state theo thời gian thực.
5. Broker restart và Wi-Fi interruption tự recover mà không cần reboot firmware.
6. Một hardware scenario kích hoạt LED/buzzer/vibration local trước backend/WebSocket confirmation.

## Ngoài phạm vi

- Fire-safety certification, intrinsically safe design hoặc sử dụng trong hazardous atmosphere.
- Camera, computer vision, TinyML, GPS, navigation hoặc victim recognition.
- Offline persistent telemetry replay.
- Remote actuator control từ dashboard.
- Thay đổi shared MQTT schema hiện có nếu chưa có contract version được phê duyệt riêng.

## Thứ tự bàn giao

1. Thêm firmware project, host-side contract fixture test và tài liệu developer.
2. Triển khai device configuration, Wi-Fi/MQTT/NTP và contract serialization.
3. Triển khai DS18B20, SOS và local actuator driver; chứng minh luồng normal và SOS.
4. Thêm MPU6050, fall detection và immobility logic kèm fixture.
5. Thêm ADS1115/MQ-7 conditioned input và calibration workflow.
6. Hoàn thiện backend cần thiết cho `IMMOBILE` và alert persistence.
7. Thực hiện bench end-to-end verification, sau đó thiết kế phần nguồn/vỏ cho wearable.
