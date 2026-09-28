#pragma once

#include <stdbool.h>

#include "esp_err.h"

esp_err_t helmet_sos_init(void);
bool helmet_sos_read_pressed(void);
