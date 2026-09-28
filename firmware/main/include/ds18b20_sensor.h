#pragma once

#include <stdbool.h>

#include "esp_err.h"

/** DS18B20 physical output range in degrees Celsius. */
bool helmet_ds18b20_temperature_valid(float temperature_c);

/** Uses the RMT 1-Wire backend on HELMET_PIN_DS18B20. External 4.7 kΩ pull-up required. */
esp_err_t helmet_ds18b20_init(void);
esp_err_t helmet_ds18b20_read_celsius(float *temperature_c);
