# Python device simulator

Simulator đóng vai trò **virtual ESP32-S3** trong giai đoạn software-first. Milestone 3 chỉ chạy kịch bản `NORMAL`, tạo telemetry/status/health, validate từng payload bằng JSON Schema trong `shared/contracts/`, rồi publish tới Mosquitto.

## Runtime dependencies

- `jsonschema`: validate contract trước mỗi publish.
- `paho-mqtt`: kết nối và publish MQTT.

Telemetry dùng QoS 0 vì có tần suất cao và payload sau sẽ thay thế payload trước. Status và health dùng QoS 1 vì được publish thưa hơn và có giá trị theo dõi trạng thái thiết bị.

Simulator không publish event trong NORMAL scenario. Backend chưa subscribe MQTT trong milestone này.

