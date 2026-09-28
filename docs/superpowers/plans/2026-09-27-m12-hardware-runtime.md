# M12 ESP32-S3 Hardware Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the buildable ESP32-S3 foundation into a bench-safe hardware publisher that reads the approved sensors, drives local actuators, and publishes the existing MQTT contract.

**Architecture:** Firmware retains local sensing → safety → actuator as the primary safety path. Wi-Fi, SNTP and MQTT form a downstream publisher path; a missing network may prevent publishing but cannot prevent a local alert. The FastAPI backend remains unchanged and consumes the existing hardware contract.

**Tech Stack:** ESP-IDF 6.1, FreeRTOS, `esp_wifi`, `esp-mqtt`, SNTP, I2C, 1-Wire, ADS1115, MPU6050, cJSON.

**Spec:** `docs/superpowers/specs/2026-09-26-hardware-integration-m12-design.md`

## Global Constraints

- Preserve topics and schema version `1.0`; source must be `HARDWARE`.
- No sensor value is published until it was actually read; unavailable temperature/CO is JSON `null`.
- A valid RFC 3339 timestamp is mandatory before publish.
- SOS/fall/critical sensor data must update local actuators before MQTT work.
- Credentials remain in `menuconfig`/NVS, never source control.
- MQ-7 is read through a voltage-safe ADS1115 input only; raw ADC voltage is not claimed to be calibrated ppm.
- No change to backend MQTT contract, safety thresholds, database model, or dashboard UI.

## File Structure

```text
firmware/main/
  connectivity.c/.h       Wi-Fi, SNTP and MQTT lifecycle/reconnect state
  sensor_manager.c/.h     Atomic sensor snapshot aggregation
  drivers/
    ds18b20.c/.h          1-Wire temperature reader
    mpu6050.c/.h          I2C IMU reader
    ads1115.c/.h          I2C ADC reader for voltage-safe MQ-7 signal
    sos.c/.h              Debounced active-low SOS input
    battery.c/.h          Calibrated voltage-to-percent boundary
  app_main.c              FreeRTOS task wiring and publication schedule
  test/                   ESP-IDF Unity fixture tests for pure logic
```

## Task 1: Connectivity runtime

**Files:** create `connectivity.c`, `include/connectivity.h`; modify `main/CMakeLists.txt`, `app_main.c`, `Kconfig.projbuild`.

- [ ] Add a state interface returning Wi-Fi, MQTT and time readiness without exposing MQTT client internals.
- [ ] Add a Wi-Fi station event handler that reconnects with bounded backoff.
- [ ] Start SNTP only once an IP address is acquired; do not publish before `helmet_time_is_valid()`.
- [ ] Configure an ESP-MQTT client using `CONFIG_HELMET_MQTT_URI` and optional username/password.
- [ ] Compile with `idf.py build`; on hardware verify broker restart recovery.

## Task 2: Safe sensor and input drivers

**Files:** create the four `drivers` modules and `sensor_manager.c/.h`; modify pin configuration and component requirements.

- [ ] Add I2C bus initialization on GPIO8/GPIO9 shared by MPU6050 and ADS1115.
- [ ] Read DS18B20 in three-wire mode on GPIO4 with explicit unavailable/error states.
- [ ] Read MPU6050 acceleration/gyro with an initialization identity check; reject a failed device.
- [ ] Read the conditioned ADS1115 MQ-7 voltage. Publish `co: null` until a documented calibration produces ppm.
- [ ] Add active-low GPIO5 SOS debounce and battery ADC divider reading on GPIO1.
- [ ] Unit-test pure conversion/debounce logic and compile the complete project.

## Task 3: Local detection and fail-safe wiring

**Files:** modify `safety_engine.c`, `sensor_manager.c`, `app_main.c`; create pure detector modules/tests.

- [ ] Evaluate every valid snapshot before any publish attempt.
- [ ] Preserve current critical temperature, CO, SOS and fall rules exactly.
- [ ] Implement fall candidate logic only with recorded MPU6050 fixtures; leave fall `false` while uncalibrated rather than guessing.
- [ ] Apply LED/buzzer/vibration states immediately, even when Wi-Fi/MQTT are disconnected.
- [ ] Test NORMAL/WARNING/CRITICAL actuator mapping and no-network local response.

## Task 4: Contract publication and bench E2E

**Files:** modify `mqtt_contract.c`, `app_main.c`, `firmware/README.md`.

- [ ] Publish telemetry every second, status every two seconds, health every five seconds after Wi-Fi+MQTT+NTP are ready.
- [ ] Publish only topic/payload pairs with identical device IDs and existing strict enum values.
- [ ] Run `mosquitto_sub -t "helmet/#" -v`; validate received payloads through backend JSON schemas.
- [ ] Confirm backend persistence, WebSocket, and dashboard show the physical device as `source=HARDWARE`.
- [ ] Record measured wiring, calibration and serial logs in the bench checklist; never call the prototype certified safety equipment.

## Acceptance Criteria

- Firmware builds and flashes to ESP32-S3.
- DS18B20, MPU6050, SOS and battery data are actual measured values.
- MQ-7 remains unavailable until calibration, never fabricated ppm.
- Critical local actuator response remains active during broker loss.
- Valid telemetry/status/health is accepted by the existing backend with no backend code change.
- Broker restart recovers publishing automatically.
