# M12 ESP32 S3 Firmware Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a testable ESP-IDF firmware foundation that can publish the existing Smart Rescue Helmet MQTT contract and drive local fail-safe actuators before physical sensors are connected.

**Architecture:** `firmware/` is an ESP-IDF project. Pure C modules model sensor snapshots, local safety decisions, actuator states and JSON payload construction; ESP-IDF adapters later read GPIO/I2C hardware and publish to MQTT. The existing backend remains the canonical remote safety/event processor, while the device evaluates the same thresholds locally to keep LED, buzzer and vibration responsive during network loss.

**Tech Stack:** ESP-IDF 5.x, FreeRTOS, esp-mqtt, cJSON, Unity C test framework, existing MQTT schema version `1.0`.

**Spec:** `docs/superpowers/specs/2026-09-26-hardware-integration-m12-design.md`

## Global Constraints

- Preserve `helmet/{device_id}/telemetry`, `status`, `health` and `event` shared topic patterns.
- Emit `schema_version: "1.0"`, `source: "HARDWARE"`, strict enum strings and RFC 3339 timestamp with timezone.
- Do not add a second Backend, database, dashboard or MQTT contract.
- Do not publish before NTP provides a compliant timestamp.
- Local actuator safety must not depend on Wi-Fi, MQTT or Backend availability.
- Use GPIO4, GPIO5, GPIO6, GPIO7, GPIO8, GPIO9, GPIO15, GPIO16, GPIO17 and GPIO1 exactly as specified in the M12 design.
- Do not commit, reset, restore, rebase, merge or checkout: the worktree contains unrelated Unity and backend changes.

---

## File structure

```text
firmware/
  CMakeLists.txt                         ESP-IDF root project
  sdkconfig.defaults                     Build defaults for ESP32-S3
  main/
    CMakeLists.txt                       Main component registration
    Kconfig.projbuild                    Firmware configuration prompts
    app_main.c                           Task startup and dependency wiring
    include/
      helmet_config.h                    GPIO, interval and threshold constants
      helmet_types.h                     Sensor, connection, risk and actuator types
      safety_engine.h                    Pure local safety interface
      actuator_controller.h              Actuator decision interface
      mqtt_contract.h                    JSON/topic construction interface
      time_sync.h                        Timestamp validity interface
    safety_engine.c                      Pure risk evaluator
    actuator_controller.c                Risk-to-actuator mapping
    mqtt_contract.c                      cJSON payload/topic builders
    time_sync.c                          NTP-ready state and RFC 3339 formatting
  test/
    test_safety_engine.c                 Safety threshold regression tests
    test_actuator_controller.c           Actuator mapping regression tests
    test_mqtt_contract.c                 Contract envelope/topic regression tests
  README.md                              Build, flash and bench safety instructions
```

## Task 1: Scaffold the ESP-IDF project and immutable configuration

**Files:**
- Create: `firmware/CMakeLists.txt`
- Create: `firmware/sdkconfig.defaults`
- Create: `firmware/main/CMakeLists.txt`
- Create: `firmware/main/Kconfig.projbuild`
- Create: `firmware/main/app_main.c`
- Create: `firmware/main/include/helmet_config.h`
- Create: `firmware/README.md`

**Interfaces:**
- Produces `CONFIG_HELMET_DEVICE_ID`, `CONFIG_HELMET_WIFI_SSID`, `CONFIG_HELMET_WIFI_PASSWORD`, `CONFIG_HELMET_MQTT_URI` and `CONFIG_HELMET_MQTT_USERNAME` configuration keys.
- Produces pin constants `HELMET_PIN_I2C_SDA`, `HELMET_PIN_I2C_SCL`, `HELMET_PIN_DS18B20`, `HELMET_PIN_SOS`, `HELMET_PIN_LED_GREEN`, `HELMET_PIN_LED_YELLOW`, `HELMET_PIN_LED_RED`, `HELMET_PIN_BUZZER`, `HELMET_PIN_VIBRATION` and `HELMET_PIN_BATTERY_ADC`.

- [ ] **Step 1: Add the minimal ESP-IDF root and component build files**

```cmake
# firmware/CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(smart_rescue_helmet)
```

Add a minimal `app_main.c` in this scaffold step so the component has a
buildable entry point before the later task wires the real runtime:

```c
void app_main(void) {}
```

```cmake
# firmware/main/CMakeLists.txt
idf_component_register(
  SRCS "app_main.c"
  INCLUDE_DIRS "include"
  REQUIRES mqtt json esp_netif nvs_flash esp_event
)
```

- [ ] **Step 2: Add Kconfig entries with empty development defaults for credentials**

```kconfig
config HELMET_DEVICE_ID
    string "Helmet device ID"
    default "FF01"

config HELMET_MQTT_URI
    string "MQTT broker URI"
    default "mqtt://192.168.1.10:1883"
```

Do not set Wi-Fi password or MQTT password defaults.

- [ ] **Step 3: Add `helmet_config.h` with the approved pin map and threshold constants**

```c
#define HELMET_PIN_I2C_SDA 8
#define HELMET_PIN_I2C_SCL 9
#define HELMET_PIN_DS18B20 4
#define HELMET_PIN_SOS 5
#define HELMET_PIN_LED_GREEN 6
#define HELMET_PIN_LED_YELLOW 7
#define HELMET_PIN_LED_RED 15
#define HELMET_PIN_BUZZER 16
#define HELMET_PIN_VIBRATION 17
#define HELMET_PIN_BATTERY_ADC 1
#define HELMET_TEMPERATURE_WARNING_C 50.0f
#define HELMET_TEMPERATURE_CRITICAL_C 60.0f
#define HELMET_CO_WARNING_PPM 50.0f
#define HELMET_CO_CRITICAL_PPM 100.0f
#define HELMET_LOW_BATTERY_PERCENT 20.0f
```

- [ ] **Step 4: Write `firmware/README.md`**

Document ESP-IDF 5.x installation, `idf.py set-target esp32s3`, `idf.py menuconfig`, `idf.py build`, `idf.py flash monitor`, the required 5 V bench supply and the rule that MQ-7 analog output must not connect directly to ESP32.

- [ ] **Step 5: Verify the clean scaffold**

Run: `idf.py set-target esp32s3 && idf.py build` from `firmware/`.

Expected: an ESP32-S3 application builds with no credentials in the repository.

## Task 2: Implement and test pure local safety decisions

**Files:**
- Create: `firmware/main/include/helmet_types.h`
- Create: `firmware/main/include/safety_engine.h`
- Create: `firmware/main/safety_engine.c`
- Create: `firmware/test/test_safety_engine.c`

**Interfaces:**
- Produces `helmet_sensor_snapshot_t`, `helmet_risk_level_t`, `helmet_movement_state_t` and `helmet_safety_result_t`.
- Produces `helmet_safety_evaluate(const helmet_sensor_snapshot_t *snapshot)`.
- Consumes configuration constants from `helmet_config.h`.

- [ ] **Step 1: Write failing Unity tests for the local safety contract**

```c
TEST_CASE("critical temperature selects critical risk", "[safety]") {
    helmet_sensor_snapshot_t snapshot = helmet_test_normal_snapshot();
    snapshot.temperature_c = 60.0f;
    snapshot.temperature_available = true;
    TEST_ASSERT_EQUAL(HELMET_RISK_CRITICAL, helmet_safety_evaluate(&snapshot).risk);
}

TEST_CASE("sos selects critical risk without network state", "[safety]") {
    helmet_sensor_snapshot_t snapshot = helmet_test_normal_snapshot();
    snapshot.sos_pressed = true;
    TEST_ASSERT_EQUAL(HELMET_RISK_CRITICAL, helmet_safety_evaluate(&snapshot).risk);
}
```

- [ ] **Step 2: Run the test target before implementation**

Run: `idf.py build` after registering the test component, then execute the Unity test app with `idf.py -C test flash monitor`.

Expected: compilation or test failure because the safety interface does not exist.

- [ ] **Step 3: Define the types and minimal pure evaluator**

```c
typedef enum { HELMET_RISK_NORMAL, HELMET_RISK_WARNING, HELMET_RISK_CRITICAL } helmet_risk_level_t;
typedef struct {
    bool temperature_available, co_available, fall_detected, immobile, sos_pressed;
    float temperature_c, co_ppm, battery_percent;
} helmet_sensor_snapshot_t;

helmet_safety_result_t helmet_safety_evaluate(const helmet_sensor_snapshot_t *snapshot);
```

The evaluator returns CRITICAL for temperature >=60, CO >=100, SOS or fall; WARNING for temperature >=50, CO >=50 or battery <=20; otherwise NORMAL. It must not read GPIO, Wi-Fi or MQTT state.

- [ ] **Step 4: Run the safety tests after implementation**

Run: `idf.py -C test flash monitor`.

Expected: normal, warning, critical, unavailable sensor and priority tests pass.

## Task 3: Implement and test local actuator mapping

**Files:**
- Create: `firmware/main/include/actuator_controller.h`
- Create: `firmware/main/actuator_controller.c`
- Create: `firmware/test/test_actuator_controller.c`

**Interfaces:**
- Consumes `helmet_risk_level_t` from `helmet_types.h`.
- Produces `helmet_actuator_state_t helmet_actuator_for_risk(helmet_risk_level_t risk)`.
- `helmet_actuator_state_t` contains booleans `led_green`, `led_yellow`, `led_red`, `buzzer_on` and `vibration_on`.

- [ ] **Step 1: Write failing mapping tests**

```c
TEST_CASE("normal maps to green and silent actuators", "[actuator]") {
    helmet_actuator_state_t state = helmet_actuator_for_risk(HELMET_RISK_NORMAL);
    TEST_ASSERT_TRUE(state.led_green);
    TEST_ASSERT_FALSE(state.buzzer_on);
    TEST_ASSERT_FALSE(state.vibration_on);
}

TEST_CASE("critical maps to red buzzer and vibration", "[actuator]") {
    helmet_actuator_state_t state = helmet_actuator_for_risk(HELMET_RISK_CRITICAL);
    TEST_ASSERT_TRUE(state.led_red);
    TEST_ASSERT_TRUE(state.buzzer_on);
    TEST_ASSERT_TRUE(state.vibration_on);
}
```

- [ ] **Step 2: Run tests and observe the missing mapping failure**

Run: `idf.py -C test flash monitor`.

Expected: test failure because `helmet_actuator_for_risk` is unavailable.

- [ ] **Step 3: Implement the pure mapping and GPIO adapter boundary**

```c
helmet_actuator_state_t helmet_actuator_for_risk(helmet_risk_level_t risk);
esp_err_t helmet_actuator_apply(const helmet_actuator_state_t *state);
```

`helmet_actuator_apply` writes only GPIO6, GPIO7, GPIO15, GPIO16 and GPIO17. It never evaluates safety or accesses MQTT.

- [ ] **Step 4: Re-run actuator tests and bench-check outputs**

Run: `idf.py -C test flash monitor`.

Expected: all actuator mapping tests pass. When a board is present, verify output voltages with a multimeter before connecting buzzer or motor.

## Task 4: Implement and test MQTT contract serialization

**Files:**
- Create: `firmware/main/include/mqtt_contract.h`
- Create: `firmware/main/mqtt_contract.c`
- Create: `firmware/test/test_mqtt_contract.c`

**Interfaces:**
- Consumes `helmet_sensor_snapshot_t`, `helmet_safety_result_t`, `helmet_connection_state_t` and `helmet_actuator_state_t`.
- Produces `char *helmet_build_telemetry_json(...)`, `char *helmet_build_status_json(...)`, `char *helmet_build_health_json(...)` and `bool helmet_build_topic(char *buffer, size_t size, const char *device_id, const char *kind)`.
- Caller frees JSON output with `cJSON_free`.

- [ ] **Step 1: Write failing contract tests using literal expected wire values**

```c
TEST_CASE("telemetry contains the required hardware envelope", "[contract]") {
    char *json = helmet_build_telemetry_json(&snapshot, &result, "2026-09-26T10:00:00+07:00", "FF01");
    cJSON *root = cJSON_Parse(json);
    TEST_ASSERT_EQUAL_STRING("1.0", cJSON_GetObjectItem(root, "schema_version")->valuestring);
    TEST_ASSERT_EQUAL_STRING("HARDWARE", cJSON_GetObjectItem(root, "source")->valuestring);
    TEST_ASSERT_EQUAL_STRING("FF01", cJSON_GetObjectItem(root, "device_id")->valuestring);
}
```

- [ ] **Step 2: Run tests before implementing builders**

Run: `idf.py -C test flash monitor`.

Expected: missing-builder failure.

- [ ] **Step 3: Build cJSON objects with only fields accepted by `shared/contracts/*.schema.json`**

Telemetry must include `sensors.temperature`, `sensors.co`, six IMU numbers, `state.movement`, `state.fall`, `state.immobile`, `state.sos`, `risk_level`, `device.battery`, `device.wifi` and `device.mqtt`. Sensor fields become JSON `null` only when unavailable. Build exact topics with `snprintf(buffer, size, "helmet/%s/%s", device_id, kind)` and reject overflow.

- [ ] **Step 4: Run firmware tests and host schema validation**

Run: `idf.py -C test flash monitor`.

Run: `docker compose run --rm --no-deps -e PYTHONPATH=/work -v "${PWD}\\backend:/work" -w /work backend pytest tests/schemas -q`.

Expected: firmware builders pass their tests; existing backend schema tests remain green.

## Task 5: Add time validity and app task wiring

**Files:**
- Create: `firmware/main/include/time_sync.h`
- Create: `firmware/main/time_sync.c`
- Create: `firmware/main/app_main.c`
- Modify: `firmware/main/CMakeLists.txt`

**Interfaces:**
- Produces `bool helmet_time_is_valid(void)` and `esp_err_t helmet_time_format_rfc3339(char *buffer, size_t size)`.
- App task consumes safety, actuator and contract interfaces and publishes only when time is valid.

- [ ] **Step 1: Write a failing timestamp test**

```c
TEST_CASE("timestamp formatter rejects time before synchronization", "[time]") {
    char timestamp[32];
    helmet_time_test_set_valid(false);
    TEST_ASSERT_FALSE(helmet_time_format_rfc3339(timestamp, sizeof(timestamp)) == ESP_OK);
}
```

- [ ] **Step 2: Run test before the time module exists**

Run: `idf.py -C test flash monitor`.

Expected: missing time-module failure.

- [ ] **Step 3: Implement NTP readiness and deterministic formatting**

The module starts SNTP only after Wi-Fi obtains an IP address. It considers time valid only after a configured minimum Unix epoch and formats `YYYY-MM-DDTHH:MM:SS+00:00`. It never uses an uninitialized clock value.

- [ ] **Step 4: Wire `app_main` in a safe order**

Initialize NVS, GPIO actuator outputs in the safe NORMAL state, network event loop and time synchronization. Run a local task every 100 ms that reads the currently injected sensor snapshot, evaluates safety and applies actuators. Run the publishing task only after `helmet_time_is_valid()` is true; it publishes telemetry every second, status every two seconds and health every five seconds.

- [ ] **Step 5: Build and flash the foundation**

Run: `idf.py set-target esp32s3 && idf.py build`.

Expected: clean ESP32-S3 firmware build. With hardware unavailable, `app_main` uses a compile-time simulation snapshot only in the bench build profile and never marks it as physical sensor data.

## Task 6: Add developer-facing provisioning and bench verification instructions

**Files:**
- Modify: `firmware/README.md`
- Modify: `README.md`

**Interfaces:**
- Documents required configuration values and the transition from simulator to `source=HARDWARE`.

- [ ] **Step 1: Document configuration and secrets**

List `HELMET_DEVICE_ID`, Wi-Fi SSID/password, MQTT URI, MQTT username/password and expected laptop LAN address. Show `idf.py menuconfig` setup without placing a real credential in code or `.env.example`.

- [ ] **Step 2: Document the bench acceptance script**

Include ordered checks: power off; verify GND; connect I2C only; flash firmware; inspect serial logs; validate MQTT with `mosquitto_sub`; verify `/health`; confirm Dashboard device; finally connect buzzer and motor through MOSFET only.

- [ ] **Step 3: Verify documentation commands against the existing stack**

Run: `docker compose config --quiet`.

Run: `Invoke-RestMethod http://localhost:8000/health`.

Expected: compose config succeeds and health returns `{"status":"ok"}`.

## Plan self-review

- Spec coverage: the plan implements the testable no-hardware foundation, local fail-safe, strict contract, NTP gate and bench procedure. Sensor drivers, IMU fall/immobility calibration, MQ-7 calibration, backend `IMMOBILE` decision and alert persistence require the physical BOM and are intentionally separate follow-up plans.
- Placeholder scan: no incomplete task markers, unspecified signatures or generic test instructions remain.
- Type consistency: `helmet_sensor_snapshot_t`, `helmet_safety_result_t`, `helmet_risk_level_t`, `helmet_actuator_state_t` and the contract builder functions are introduced before later tasks consume them.
