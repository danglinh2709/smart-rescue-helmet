#include "sos_driver.h"

#include "driver/gpio.h"
#include "esp_timer.h"
#include "helmet_config.h"
#include "sos.h"

static helmet_sos_debouncer_t debouncer;

esp_err_t helmet_sos_init(void)
{
    const gpio_config_t config = {
        .pin_bit_mask = 1ULL << HELMET_PIN_SOS,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    debouncer = helmet_sos_debouncer_initial();
    return gpio_config(&config);
}

bool helmet_sos_read_pressed(void)
{
    const bool pin_high = gpio_get_level(HELMET_PIN_SOS) != 0;
    const uint32_t now_ms = (uint32_t)(esp_timer_get_time() / 1000);
    return helmet_sos_debouncer_update(&debouncer, pin_high, now_ms);
}
