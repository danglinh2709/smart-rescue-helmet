#pragma once

#include <stdbool.h>
#include <stddef.h>

/** Returns true only when the RTC contains a plausibly synchronized UTC time. */
bool helmet_time_is_valid(void);

/** Formats UTC as RFC 3339 `YYYY-MM-DDTHH:MM:SS+00:00`; false before sync. */
bool helmet_time_format_rfc3339(char *buffer, size_t size);
