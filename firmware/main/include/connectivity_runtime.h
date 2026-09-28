#pragma once

#include <stdbool.h>

#include "esp_err.h"

esp_err_t helmet_connectivity_start(void);
bool helmet_connectivity_wifi_connected(void);
bool helmet_connectivity_mqtt_connected(void);
esp_err_t helmet_connectivity_publish(const char *topic, const char *payload, int qos);
