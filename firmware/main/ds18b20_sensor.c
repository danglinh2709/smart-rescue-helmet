#include "ds18b20_sensor.h"

#include "ds18b20.h"
#include "esp_check.h"
#include "helmet_config.h"
#include "onewire_bus.h"

static onewire_bus_handle_t bus;
static ds18b20_device_handle_t device;

bool helmet_ds18b20_temperature_valid(float temperature_c)
{
    return temperature_c >= -55.0f && temperature_c <= 125.0f;
}

esp_err_t helmet_ds18b20_init(void)
{
    if (device != NULL) {
        return ESP_OK;
    }
    const onewire_bus_config_t bus_config = {
        .bus_gpio_num = HELMET_PIN_DS18B20,
        .flags.en_pull_up = false,
    };
    const onewire_bus_rmt_config_t rmt_config = { .max_rx_bytes = 10 };
    ESP_RETURN_ON_ERROR(onewire_new_bus_rmt(&bus_config, &rmt_config, &bus),
        "ds18b20", "create 1-wire bus");
    ESP_RETURN_ON_ERROR(onewire_bus_reset(bus), "ds18b20", "sensor presence check");
    const ds18b20_config_t config = {};
    return ds18b20_new_single_device(bus, &config, &device);
}

esp_err_t helmet_ds18b20_read_celsius(float *temperature_c)
{
    if (device == NULL || temperature_c == NULL) {
        return ESP_ERR_INVALID_STATE;
    }
    ESP_RETURN_ON_ERROR(ds18b20_trigger_temperature_conversion(device),
        "ds18b20", "temperature conversion");
    ESP_RETURN_ON_ERROR(ds18b20_get_temperature(device, temperature_c),
        "ds18b20", "temperature read");
    return helmet_ds18b20_temperature_valid(*temperature_c) ? ESP_OK : ESP_FAIL;
}
