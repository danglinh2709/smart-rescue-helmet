#include <assert.h>

#include "sensor_manager.h"

int main(void)
{
    helmet_sensor_snapshot_t snapshot = helmet_sensor_snapshot_unavailable();
    assert(!snapshot.temperature_available);
    assert(!snapshot.co_available);
    assert(snapshot.battery_percent == 0.0f);
    assert(snapshot.movement == HELMET_MOVEMENT_UNKNOWN);

    snapshot = helmet_sensor_manager_read();
    assert(!snapshot.temperature_available);
    assert(!snapshot.co_available);
    assert(!snapshot.battery_available);
    assert(!snapshot.imu_available);
    return 0;
}
