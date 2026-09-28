#include <assert.h>

#include "connectivity.h"

int main(void)
{
    assert(!helmet_connectivity_publish_ready(false, false, false));
    assert(!helmet_connectivity_publish_ready(true, false, true));
    assert(!helmet_connectivity_publish_ready(true, true, false));
    assert(helmet_connectivity_publish_ready(true, true, true));
    assert(helmet_connectivity_retry_delay_ms(0) == 1000);
    assert(helmet_connectivity_retry_delay_ms(1) == 2000);
    assert(helmet_connectivity_retry_delay_ms(4) == 16000);
    assert(helmet_connectivity_retry_delay_ms(8) == 30000);
    return 0;
}
