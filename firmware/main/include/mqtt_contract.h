#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "helmet_types.h"

bool helmet_build_topic(char *buffer, size_t size, const char *device_id, const char *kind);

char *helmet_build_telemetry_json(const helmet_sensor_snapshot_t *snapshot,
    const helmet_safety_result_t *safety, const char *timestamp,
    const char *device_id, helmet_connection_state_t wifi,
    helmet_connection_state_t mqtt);

char *helmet_build_status_json(const helmet_sensor_snapshot_t *snapshot,
    const helmet_safety_result_t *safety, const char *timestamp,
    const char *device_id);

char *helmet_build_health_json(float battery_percent, uint32_t uptime_seconds,
    const char *timestamp, const char *device_id, helmet_connection_state_t wifi,
    helmet_connection_state_t mqtt, helmet_sensor_status_t temperature,
    helmet_sensor_status_t co, helmet_sensor_status_t imu);
