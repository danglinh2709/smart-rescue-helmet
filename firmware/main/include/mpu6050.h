#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"
#include "helmet_types.h"

bool helmet_mpu6050_identity_valid(uint8_t who_am_i);
esp_err_t helmet_mpu6050_init(uint8_t address);
esp_err_t helmet_mpu6050_read(helmet_imu_reading_t *reading);
