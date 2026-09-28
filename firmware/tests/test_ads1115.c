#include <assert.h>

#include "ads1115.h"

int main(void)
{
    assert(helmet_ads1115_raw_to_volts(0) == 0.0f);
    assert(helmet_ads1115_raw_to_volts(32767) > 4.095f);
    assert(helmet_ads1115_raw_to_volts(-32768) == -4.096f);
    return 0;
}
