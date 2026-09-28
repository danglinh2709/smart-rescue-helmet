#pragma once

#include <stdbool.h>

#include "esp_err.h"

float helmet_battery_percent_from_pack_mv(int pack_mv, int empty_mv, int full_mv);
esp_err_t helmet_battery_init(void);
esp_err_t helmet_battery_read_percent(float *percent);
