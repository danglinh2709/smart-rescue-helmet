#include <assert.h>

#include "battery.h"

int main(void)
{
    assert(helmet_battery_percent_from_pack_mv(3300, 3300, 4200) == 0.0f);
    assert(helmet_battery_percent_from_pack_mv(4200, 3300, 4200) == 100.0f);
    assert(helmet_battery_percent_from_pack_mv(3750, 3300, 4200) == 50.0f);
    return 0;
}
