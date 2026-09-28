#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"

/**
 * The hardware CO path is MQ-7 -> safe 3.3 V signal conditioning -> ADS1115 AIN0.
 * This driver reports electrical voltage only. MQ-7 ppm conversion remains disabled
 * until the production module has a documented heater cycle and calibration curve.
 */
bool helmet_ads1115_address_valid(uint8_t address);
float helmet_ads1115_raw_to_volts(int16_t raw);
esp_err_t helmet_ads1115_init(uint8_t address);
esp_err_t helmet_ads1115_read_ain0_volts(float *volts);
