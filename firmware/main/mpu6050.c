#include "mpu6050.h"

#include "esp_check.h"
#include "i2c_bus.h"
#include "i2c_runtime.h"

#define MPU6050_WHO_AM_I 0x75
#define MPU6050_PWR_MGMT_1 0x6B
#define MPU6050_ACCEL_XOUT_H 0x3B

static i2c_master_dev_handle_t device;

bool helmet_mpu6050_identity_valid(uint8_t who_am_i)
{
    return who_am_i == 0x68;
}

esp_err_t helmet_mpu6050_init(uint8_t address)
{
    if (!helmet_i2c_is_mpu6050_address(address) || helmet_i2c_bus() == NULL) return ESP_ERR_INVALID_ARG;
    const i2c_device_config_t config = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = address,
        .scl_speed_hz = 400000,
    };
    ESP_RETURN_ON_ERROR(i2c_master_bus_add_device(helmet_i2c_bus(), &config, &device), "mpu6050", "add device");
    uint8_t register_address = MPU6050_WHO_AM_I, identity = 0;
    ESP_RETURN_ON_ERROR(i2c_master_transmit_receive(device, &register_address, 1, &identity, 1, 100), "mpu6050", "identity read");
    if (!helmet_mpu6050_identity_valid(identity)) return ESP_ERR_NOT_FOUND;
    const uint8_t wake[] = { MPU6050_PWR_MGMT_1, 0x00 };
    return i2c_master_transmit(device, wake, sizeof(wake), 100);
}

esp_err_t helmet_mpu6050_read(helmet_imu_reading_t *reading)
{
    if (device == NULL || reading == NULL) return ESP_ERR_INVALID_STATE;
    uint8_t reg = MPU6050_ACCEL_XOUT_H, raw[14];
    ESP_RETURN_ON_ERROR(i2c_master_transmit_receive(device, &reg, 1, raw, sizeof(raw), 100), "mpu6050", "read");
    const int16_t ax = (int16_t)((raw[0] << 8) | raw[1]);
    const int16_t ay = (int16_t)((raw[2] << 8) | raw[3]);
    const int16_t az = (int16_t)((raw[4] << 8) | raw[5]);
    const int16_t gx = (int16_t)((raw[8] << 8) | raw[9]);
    const int16_t gy = (int16_t)((raw[10] << 8) | raw[11]);
    const int16_t gz = (int16_t)((raw[12] << 8) | raw[13]);
    *reading = (helmet_imu_reading_t){ ax / 16384.0f, ay / 16384.0f, az / 16384.0f, gx / 131.0f, gy / 131.0f, gz / 131.0f };
    return ESP_OK;
}
