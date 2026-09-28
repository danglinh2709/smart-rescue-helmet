#include "time_sync.h"

#include <time.h>

/* 2025-01-01T00:00:00Z: rejects ESP's initial epoch until SNTP sets the RTC. */
#define HELMET_MIN_VALID_UNIX_TIME 1735689600LL

bool helmet_time_is_valid(void)
{
    return (long long)time(NULL) >= HELMET_MIN_VALID_UNIX_TIME;
}

bool helmet_time_format_rfc3339(char *buffer, size_t size)
{
    if (buffer == NULL || size < 26 || !helmet_time_is_valid()) {
        return false;
    }

    const time_t now = time(NULL);
    struct tm utc_time;
    if (gmtime_r(&now, &utc_time) == NULL) {
        return false;
    }
    return strftime(buffer, size, "%Y-%m-%dT%H:%M:%S+00:00", &utc_time) > 0;
}
