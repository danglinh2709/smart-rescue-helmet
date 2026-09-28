#include "ads1115.h"

#include "esp_check.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "i2c_bus.h"
#include "i2c_runtime.h"

#define ADS1115_REG_CONVERSION 0x00
#define ADS1115_REG_CONFIG 0x01
#define ADS1115_CONFIG_AIN0_SINGLE_SHOT 0xC383
#define ADS1115_FULL_SCALE_VOLTS 4.096f

static i2c_master_dev_handle_t device;

bool helmet_ads1115_address_valid(uint8_t address)
{
    return helmet_i2c_is_ads1115_address(address);
}

float helmet_ads1115_raw_to_volts(int16_t raw)
{
    return (float)raw * (ADS1115_FULL_SCALE_VOLTS / 32768.0f);
}

esp_err_t helmet_ads1115_init(uint8_t address)
{
    if (!helmet_ads1115_address_valid(address) || helmet_i2c_bus() == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    const i2c_device_config_t config = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = address,
        .scl_speed_hz = 400000,
    };
    return i2c_master_bus_add_device(helmet_i2c_bus(), &config, &device);
}

esp_err_t helmet_ads1115_read_ain0_volts(float *volts)
{
    if (device == NULL || volts == NULL) {
        return ESP_ERR_INVALID_STATE;
    }
    const uint8_t config[] = {
        ADS1115_REG_CONFIG,
        (uint8_t)(ADS1115_CONFIG_AIN0_SINGLE_SHOT >> 8),
        (uint8_t)ADS1115_CONFIG_AIN0_SINGLE_SHOT,
    };
    ESP_RETURN_ON_ERROR(i2c_master_transmit(device, config, sizeof(config), 100),
        "ads1115", "start conversion");
    vTaskDelay(pdMS_TO_TICKS(10));

    const uint8_t conversion_register = ADS1115_REG_CONVERSION;
    uint8_t raw[2] = { 0 };
    ESP_RETURN_ON_ERROR(i2c_master_transmit_receive(device, &conversion_register, 1,
        raw, sizeof(raw), 100), "ads1115", "read conversion");
    const int16_t value = (int16_t)((raw[0] << 8) | raw[1]);
    *volts = helmet_ads1115_raw_to_volts(value);
    return ESP_OK;
}
