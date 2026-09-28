#include <assert.h>
#include <stdbool.h>

#include "helmet_config.h"
#include "safety_engine.h"
#include "sensor_manager.h"

static helmet_sensor_snapshot_t normal_snapshot(void)
{
    return (helmet_sensor_snapshot_t){
        .temperature_available = true,
        .co_available = true,
        .battery_available = true,
        .temperature_c = 30.0f,
        .co_ppm = 5.0f,
        .battery_percent = 85.0f,
    };
}

int main(void)
{
    helmet_sensor_snapshot_t snapshot = normal_snapshot();
    assert(helmet_safety_evaluate(&snapshot).risk == HELMET_RISK_NORMAL);

    snapshot.temperature_c = HELMET_TEMPERATURE_WARNING_C;
    assert(helmet_safety_evaluate(&snapshot).risk == HELMET_RISK_WARNING);

    snapshot = normal_snapshot();
    snapshot.temperature_c = HELMET_TEMPERATURE_CRITICAL_C;
    assert(helmet_safety_evaluate(&snapshot).risk == HELMET_RISK_CRITICAL);

    snapshot = normal_snapshot();
    snapshot.co_ppm = HELMET_CO_CRITICAL_PPM;
    assert(helmet_safety_evaluate(&snapshot).risk == HELMET_RISK_CRITICAL);

    snapshot = normal_snapshot();
    snapshot.sos_pressed = true;
    assert(helmet_safety_evaluate(&snapshot).risk == HELMET_RISK_CRITICAL);

    snapshot = normal_snapshot();
    snapshot.fall_detected = true;
    assert(helmet_safety_evaluate(&snapshot).risk == HELMET_RISK_CRITICAL);

    snapshot = helmet_sensor_snapshot_unavailable();
    assert(helmet_safety_evaluate(&snapshot).risk == HELMET_RISK_NORMAL);

    snapshot = normal_snapshot();
    snapshot.battery_percent = HELMET_LOW_BATTERY_PERCENT;
    assert(helmet_safety_evaluate(&snapshot).risk == HELMET_RISK_WARNING);

    return 0;
}
