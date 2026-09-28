#include "i2c_runtime.h"

#include "helmet_config.h"

static i2c_master_bus_handle_t bus_handle;

esp_err_t helmet_i2c_init(void)
{
    if (bus_handle != NULL) {
        return ESP_OK;
    }
    const i2c_master_bus_config_t config = {
        .i2c_port = -1,
        .sda_io_num = HELMET_PIN_I2C_SDA,
        .scl_io_num = HELMET_PIN_I2C_SCL,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .trans_queue_depth = 0,
        .flags.enable_internal_pullup = 1,
    };
    return i2c_new_master_bus(&config, &bus_handle);
}

i2c_master_bus_handle_t helmet_i2c_bus(void)
{
    return bus_handle;
}
