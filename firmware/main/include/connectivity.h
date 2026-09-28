#pragma once

#include <stdbool.h>
#include <stdint.h>

/** Pure readiness gate used by publication scheduling and host-independent tests. */
bool helmet_connectivity_publish_ready(bool wifi_connected, bool mqtt_connected,
    bool time_valid);

/** Returns the bounded Wi-Fi retry delay for a zero-based failed attempt. */
uint32_t helmet_connectivity_retry_delay_ms(uint8_t attempt);
