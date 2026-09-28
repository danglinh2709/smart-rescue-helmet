#pragma once

#include "helmet_types.h"

/**
 * Evaluates only the latest sensor snapshot. This function has no GPIO,
 * Wi-Fi, MQTT, FreeRTOS or Backend dependency so it remains usable offline.
 */
helmet_safety_result_t helmet_safety_evaluate(const helmet_sensor_snapshot_t *snapshot);
