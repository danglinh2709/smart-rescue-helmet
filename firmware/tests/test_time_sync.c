#include <assert.h>

#include "time_sync.h"

int main(void)
{
    char timestamp[32];
    assert(!helmet_time_format_rfc3339(timestamp, sizeof(timestamp)));
    return 0;
}
