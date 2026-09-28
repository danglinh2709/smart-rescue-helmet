#pragma once

#include "driver/i2c_master.h"
#include "esp_err.h"

esp_err_t helmet_i2c_init(void);
i2c_master_bus_handle_t helmet_i2c_bus(void);
