#include "safety_engine.h"

#include <stddef.h>

#include "helmet_config.h"

helmet_safety_result_t helmet_safety_evaluate(const helmet_sensor_snapshot_t *snapshot)
{
    helmet_safety_result_t result = { .risk = HELMET_RISK_NORMAL };

    if (snapshot == NULL) {
        return result;
    }

    result.temperature_critical = snapshot->temperature_available &&
        snapshot->temperature_c >= HELMET_TEMPERATURE_CRITICAL_C;
    result.temperature_warning = snapshot->temperature_available &&
        snapshot->temperature_c >= HELMET_TEMPERATURE_WARNING_C;
    result.co_critical = snapshot->co_available &&
        snapshot->co_ppm >= HELMET_CO_CRITICAL_PPM;
    result.co_warning = snapshot->co_available &&
        snapshot->co_ppm >= HELMET_CO_WARNING_PPM;
    result.low_battery = snapshot->battery_available &&
        snapshot->battery_percent <= HELMET_LOW_BATTERY_PERCENT;
    result.fall_critical = snapshot->fall_detected;
    result.sos_critical = snapshot->sos_pressed;

    if (result.temperature_critical || result.co_critical ||
        result.fall_critical || result.sos_critical) {
        result.risk = HELMET_RISK_CRITICAL;
    } else if (result.temperature_warning || result.co_warning || result.low_battery) {
        result.risk = HELMET_RISK_WARNING;
    }

    return result;
}
