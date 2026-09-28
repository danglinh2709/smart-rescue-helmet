#include <assert.h>

#include "ds18b20_sensor.h"

int main(void)
{
    assert(helmet_ds18b20_temperature_valid(-55.0f));
    assert(helmet_ds18b20_temperature_valid(125.0f));
    assert(!helmet_ds18b20_temperature_valid(-55.1f));
    assert(!helmet_ds18b20_temperature_valid(125.1f));
    return 0;
}
