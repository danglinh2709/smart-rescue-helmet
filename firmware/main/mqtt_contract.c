#include "mqtt_contract.h"

#include <stdio.h>
#include <string.h>

#include "cJSON.h"
#include "helmet_config.h"

static const char *risk_string(helmet_risk_level_t risk)
{
    static const char *values[] = { "NORMAL", "WARNING", "CRITICAL" };
    return risk <= HELMET_RISK_CRITICAL ? values[risk] : "NORMAL";
}

static const char *movement_string(helmet_movement_state_t movement)
{
    static const char *values[] = {
        "UNKNOWN", "STATIONARY", "WALKING", "RUNNING", "CRAWLING",
        "UNUSUAL_MOVEMENT", "FALL", "IMMOBILE",
    };
    return movement <= HELMET_MOVEMENT_IMMOBILE ? values[movement] : "UNKNOWN";
}

static const char *connection_string(helmet_connection_state_t state)
{
    return state == HELMET_CONNECTION_CONNECTED ? "CONNECTED" : "DISCONNECTED";
}

static const char *sensor_status_string(helmet_sensor_status_t status)
{
    static const char *values[] = { "OK", "ERROR", "UNAVAILABLE" };
    return status <= HELMET_SENSOR_UNAVAILABLE ? values[status] : "ERROR";
}

static bool device_id_is_valid(const char *device_id)
{
    if (device_id == NULL) {
        return false;
    }
    const size_t length = strlen(device_id);
    if (length < 3 || length > 32 || device_id[0] < 'A' || device_id[0] > 'Z') {
        return false;
    }
    for (size_t index = 1; index < length; ++index) {
        const char value = device_id[index];
        const bool uppercase_letter = value >= 'A' && value <= 'Z';
        const bool digit = value >= '0' && value <= '9';
        if (!uppercase_letter && !digit && value != '_' && value != '-') {
            return false;
        }
    }
    return true;
}

static cJSON *message_base(const char *timestamp, const char *device_id)
{
    if (timestamp == NULL || device_id == NULL || timestamp[0] == '\0' || device_id[0] == '\0') {
        return NULL;
    }
    cJSON *root = cJSON_CreateObject();
    if (root == NULL) {
        return NULL;
    }
    cJSON_AddStringToObject(root, "schema_version", HELMET_SCHEMA_VERSION);
    cJSON_AddStringToObject(root, "device_id", device_id);
    cJSON_AddStringToObject(root, "timestamp", timestamp);
    cJSON_AddStringToObject(root, "source", HELMET_SOURCE_HARDWARE);
    return root;
}

static char *print_and_delete(cJSON *root)
{
    if (root == NULL) {
        return NULL;
    }
    char *json = cJSON_PrintUnformatted(root);
    cJSON_Delete(root);
    return json;
}

bool helmet_build_topic(char *buffer, size_t size, const char *device_id, const char *kind)
{
    if (buffer == NULL || size == 0 || kind == NULL || !device_id_is_valid(device_id) ||
        kind[0] == '\0') {
        return false;
    }
    int written = snprintf(buffer, size, "helmet/%s/%s", device_id, kind);
    return written >= 0 && (size_t)written < size;
}

char *helmet_build_telemetry_json(const helmet_sensor_snapshot_t *snapshot,
    const helmet_safety_result_t *safety, const char *timestamp,
    const char *device_id, helmet_connection_state_t wifi,
    helmet_connection_state_t mqtt)
{
    if (snapshot == NULL || safety == NULL) {
        return NULL;
    }
    cJSON *root = message_base(timestamp, device_id);
    if (root == NULL) {
        return NULL;
    }
    cJSON *sensors = cJSON_AddObjectToObject(root, "sensors");
    snapshot->temperature_available ? cJSON_AddNumberToObject(sensors, "temperature", snapshot->temperature_c) : cJSON_AddNullToObject(sensors, "temperature");
    snapshot->co_available ? cJSON_AddNumberToObject(sensors, "co", snapshot->co_ppm) : cJSON_AddNullToObject(sensors, "co");
    cJSON *imu = cJSON_AddObjectToObject(sensors, "imu");
    cJSON_AddNumberToObject(imu, "ax", snapshot->imu.ax);
    cJSON_AddNumberToObject(imu, "ay", snapshot->imu.ay);
    cJSON_AddNumberToObject(imu, "az", snapshot->imu.az);
    cJSON_AddNumberToObject(imu, "gx", snapshot->imu.gx);
    cJSON_AddNumberToObject(imu, "gy", snapshot->imu.gy);
    cJSON_AddNumberToObject(imu, "gz", snapshot->imu.gz);
    cJSON *state = cJSON_AddObjectToObject(root, "state");
    cJSON_AddStringToObject(state, "movement", movement_string(snapshot->movement));
    cJSON_AddBoolToObject(state, "fall", snapshot->fall_detected);
    cJSON_AddBoolToObject(state, "immobile", snapshot->immobile);
    cJSON_AddBoolToObject(state, "sos", snapshot->sos_pressed);
    cJSON_AddStringToObject(root, "risk_level", risk_string(safety->risk));
    cJSON *device = cJSON_AddObjectToObject(root, "device");
    cJSON_AddNumberToObject(device, "battery", snapshot->battery_percent);
    cJSON_AddStringToObject(device, "wifi", connection_string(wifi));
    cJSON_AddStringToObject(device, "mqtt", connection_string(mqtt));
    return print_and_delete(root);
}

char *helmet_build_status_json(const helmet_sensor_snapshot_t *snapshot,
    const helmet_safety_result_t *safety, const char *timestamp,
    const char *device_id)
{
    if (snapshot == NULL || safety == NULL) {
        return NULL;
    }
    cJSON *root = message_base(timestamp, device_id);
    if (root == NULL) {
        return NULL;
    }
    cJSON_AddStringToObject(root, "device_status", "ONLINE");
    cJSON_AddStringToObject(root, "risk_level", risk_string(safety->risk));
    cJSON_AddStringToObject(root, "movement", movement_string(snapshot->movement));
    cJSON_AddBoolToObject(root, "fall", snapshot->fall_detected);
    cJSON_AddBoolToObject(root, "immobile", snapshot->immobile);
    cJSON_AddBoolToObject(root, "sos", snapshot->sos_pressed);
    return print_and_delete(root);
}

char *helmet_build_health_json(float battery_percent, uint32_t uptime_seconds,
    const char *timestamp, const char *device_id, helmet_connection_state_t wifi,
    helmet_connection_state_t mqtt, helmet_sensor_status_t temperature,
    helmet_sensor_status_t co, helmet_sensor_status_t imu)
{
    cJSON *root = message_base(timestamp, device_id);
    if (root == NULL) {
        return NULL;
    }
    cJSON_AddNumberToObject(root, "battery", battery_percent);
    cJSON_AddNumberToObject(root, "uptime_seconds", uptime_seconds);
    cJSON_AddStringToObject(root, "wifi", connection_string(wifi));
    cJSON_AddStringToObject(root, "mqtt", connection_string(mqtt));
    cJSON *sensors = cJSON_AddObjectToObject(root, "sensors");
    cJSON_AddStringToObject(sensors, "temperature", sensor_status_string(temperature));
    cJSON_AddStringToObject(sensors, "co", sensor_status_string(co));
    cJSON_AddStringToObject(sensors, "imu", sensor_status_string(imu));
    return print_and_delete(root);
}
