#pragma once

#include <stdbool.h>
#include <stdint.h>

bool helmet_i2c_is_mpu6050_address(uint8_t address);
bool helmet_i2c_is_ads1115_address(uint8_t address);
