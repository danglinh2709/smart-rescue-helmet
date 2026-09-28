#include "sensor_manager.h"

#include "esp_log.h"
#include "esp_timer.h"
#include "battery.h"
#include "ds18b20_sensor.h"
#include "i2c_runtime.h"
#include "mpu6050.h"
#include "sos_driver.h"

static const char *TAG = "sensor_manager";
static bool initialized;
static bool imu_available;
static bool temperature_driver_ready;
static bool temperature_sample_valid;
static int64_t last_temperature_sample_us;
static float last_temperature_c;
static bool battery_driver_ready;
static bool battery_sample_valid;
static int64_t last_battery_sample_us;
static float last_battery_percent;

helmet_sensor_snapshot_t helmet_sensor_snapshot_unavailable(void)
{
    return (helmet_sensor_snapshot_t){
        .temperature_available = false,
        .co_available = false,
        .battery_percent = 0.0f,
        .movement = HELMET_MOVEMENT_UNKNOWN,
    };
}

esp_err_t helmet_sensor_manager_init(void)
{
    const esp_err_t sos_result = helmet_sos_init();
    if (sos_result != ESP_OK) {
        return sos_result;
    }
    initialized = true;

    const esp_err_t battery_result = helmet_battery_init();
    battery_driver_ready = battery_result == ESP_OK;
    if (!battery_driver_ready) {
        ESP_LOGW(TAG, "Battery ADC unavailable (%s)", esp_err_to_name(battery_result));
    }

    const esp_err_t temperature_result = helmet_ds18b20_init();
    temperature_driver_ready = temperature_result == ESP_OK;
    if (!temperature_driver_ready) {
        ESP_LOGW(TAG, "DS18B20 unavailable (%s)", esp_err_to_name(temperature_result));
    }

    const esp_err_t i2c_result = helmet_i2c_init();
    if (i2c_result != ESP_OK) {
        ESP_LOGW(TAG, "I2C bus unavailable (%s); IMU remains unavailable", esp_err_to_name(i2c_result));
        return ESP_OK;
    }
    const esp_err_t mpu_result = helmet_mpu6050_init(0x68);
    imu_available = mpu_result == ESP_OK;
    if (!imu_available) {
        ESP_LOGW(TAG, "MPU6050 unavailable (%s)", esp_err_to_name(mpu_result));
    }
    return ESP_OK;
}

helmet_sensor_snapshot_t helmet_sensor_manager_read(void)
{
    helmet_sensor_snapshot_t snapshot = helmet_sensor_snapshot_unavailable();
    if (!initialized) {
        return snapshot;
    }
    snapshot.sos_pressed = helmet_sos_read_pressed();
    if (temperature_driver_ready &&
        esp_timer_get_time() - last_temperature_sample_us >= 1000000) {
        last_temperature_sample_us = esp_timer_get_time();
        temperature_sample_valid = helmet_ds18b20_read_celsius(&last_temperature_c) == ESP_OK;
        if (!temperature_sample_valid) {
            ESP_LOGW(TAG, "DS18B20 read failed; temperature unavailable until next sample");
        }
    }
    if (temperature_sample_valid) {
        snapshot.temperature_available = true;
        snapshot.temperature_c = last_temperature_c;
    }
    if (battery_driver_ready && esp_timer_get_time() - last_battery_sample_us >= 1000000) {
        last_battery_sample_us = esp_timer_get_time();
        battery_sample_valid = helmet_battery_read_percent(&last_battery_percent) == ESP_OK;
        if (!battery_sample_valid) {
            ESP_LOGW(TAG, "Battery ADC read failed; battery unavailable until next sample");
        }
    }
    if (battery_sample_valid) {
        snapshot.battery_available = true;
        snapshot.battery_percent = last_battery_percent;
    }
    if (imu_available) {
        if (helmet_mpu6050_read(&snapshot.imu) == ESP_OK) {
            snapshot.imu_available = true;
        } else {
            imu_available = false;
            ESP_LOGW(TAG, "MPU6050 read failed; marking IMU unavailable");
        }
    }
    return snapshot;
}
