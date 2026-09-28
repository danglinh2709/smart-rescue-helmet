#include <stdint.h>

#include "cJSON.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"

#include "actuator_controller.h"
#include "actuator_driver.h"
#include "connectivity.h"
#include "connectivity_runtime.h"
#include "mqtt_contract.h"
#include "safety_engine.h"
#include "sensor_manager.h"
#include "time_sync.h"

static const char *TAG = "smart_rescue_helmet";

static void publish_payload(const char *kind, char *payload)
{
    if (payload == NULL) {
        ESP_LOGW(TAG, "Cannot build %s payload", kind);
        return;
    }
    char topic[80];
    if (!helmet_build_topic(topic, sizeof(topic), CONFIG_HELMET_DEVICE_ID, kind) ||
        helmet_connectivity_publish(topic, payload, 1) != ESP_OK) {
        ESP_LOGW(TAG, "Publish failed for %s", kind);
    }
    cJSON_free(payload);
}

static void publish_updates(const helmet_sensor_snapshot_t *snapshot,
    const helmet_safety_result_t *safety)
{
    static int64_t last_telemetry_us;
    static int64_t last_status_us;
    static int64_t last_health_us;
    if (!helmet_connectivity_publish_ready(helmet_connectivity_wifi_connected(),
        helmet_connectivity_mqtt_connected(), helmet_time_is_valid())) {
        return;
    }
    char timestamp[32];
    if (!helmet_time_format_rfc3339(timestamp, sizeof(timestamp))) {
        return;
    }
    const int64_t now_us = esp_timer_get_time();
    if (now_us - last_status_us >= 2000000) {
        publish_payload("status", helmet_build_status_json(snapshot, safety, timestamp,
            CONFIG_HELMET_DEVICE_ID));
        last_status_us = now_us;
    }
    if (snapshot->battery_available && snapshot->imu_available &&
        now_us - last_telemetry_us >= 1000000) {
        publish_payload("telemetry", helmet_build_telemetry_json(snapshot, safety, timestamp,
            CONFIG_HELMET_DEVICE_ID, HELMET_CONNECTION_CONNECTED,
            HELMET_CONNECTION_CONNECTED));
        last_telemetry_us = now_us;
    }
    if (snapshot->battery_available && now_us - last_health_us >= 5000000) {
        publish_payload("health", helmet_build_health_json(snapshot->battery_percent,
            (uint32_t)(now_us / 1000000), timestamp, CONFIG_HELMET_DEVICE_ID,
            HELMET_CONNECTION_CONNECTED, HELMET_CONNECTION_CONNECTED,
            snapshot->temperature_available ? HELMET_SENSOR_OK : HELMET_SENSOR_UNAVAILABLE,
            snapshot->co_available ? HELMET_SENSOR_OK : HELMET_SENSOR_UNAVAILABLE,
            snapshot->imu_available ? HELMET_SENSOR_OK : HELMET_SENSOR_UNAVAILABLE));
        last_health_us = now_us;
    }
}

static void local_safety_task(void *argument)
{
    (void)argument;
    helmet_risk_level_t previous_risk = HELMET_RISK_NORMAL;
    for (;;) {
        const helmet_sensor_snapshot_t snapshot = helmet_sensor_manager_read();
        const helmet_safety_result_t safety = helmet_safety_evaluate(&snapshot);
        const helmet_actuator_state_t actuators = helmet_actuator_for_risk(safety.risk);
        (void)helmet_actuator_apply(&actuators);
        publish_updates(&snapshot, &safety);
        if (safety.risk != previous_risk) {
            ESP_LOGW(TAG, "Local risk state changed to %d", safety.risk);
            previous_risk = safety.risk;
        }
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void app_main(void)
{
    ESP_LOGI(TAG, "Smart Rescue Helmet firmware foundation starting");
    ESP_ERROR_CHECK(helmet_actuator_init());
    ESP_ERROR_CHECK(helmet_sensor_manager_init());
    ESP_ERROR_CHECK(helmet_connectivity_start());
    xTaskCreate(local_safety_task, "helmet_local_safety", 3072, NULL, 5, NULL);
}
