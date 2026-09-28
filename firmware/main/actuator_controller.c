#include "actuator_controller.h"
#include "actuator_driver.h"

#include "driver/gpio.h"
#include "helmet_config.h"

helmet_actuator_state_t helmet_actuator_for_risk(helmet_risk_level_t risk)
{
    switch (risk) {
    case HELMET_RISK_CRITICAL:
        return (helmet_actuator_state_t){ .led_red = true, .buzzer_on = true, .vibration_on = true };
    case HELMET_RISK_WARNING:
        return (helmet_actuator_state_t){ .led_yellow = true };
    case HELMET_RISK_NORMAL:
    default:
        return (helmet_actuator_state_t){ .led_green = true };
    }
}

esp_err_t helmet_actuator_apply(const helmet_actuator_state_t *state)
{
    if (state == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    const gpio_num_t pins[] = {
        HELMET_PIN_LED_GREEN, HELMET_PIN_LED_YELLOW, HELMET_PIN_LED_RED,
        HELMET_PIN_BUZZER, HELMET_PIN_VIBRATION,
    };
    const int levels[] = {
        state->led_green, state->led_yellow, state->led_red,
        state->buzzer_on, state->vibration_on,
    };

    for (size_t index = 0; index < sizeof(pins) / sizeof(pins[0]); ++index) {
        esp_err_t result = gpio_set_level(pins[index], levels[index]);
        if (result != ESP_OK) {
            return result;
        }
    }
    return ESP_OK;
}

esp_err_t helmet_actuator_init(void)
{
    const uint64_t mask = (1ULL << HELMET_PIN_LED_GREEN) |
        (1ULL << HELMET_PIN_LED_YELLOW) |
        (1ULL << HELMET_PIN_LED_RED) |
        (1ULL << HELMET_PIN_BUZZER) |
        (1ULL << HELMET_PIN_VIBRATION);
    const gpio_config_t config = {
        .pin_bit_mask = mask,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    esp_err_t result = gpio_config(&config);
    if (result != ESP_OK) {
        return result;
    }
    const helmet_actuator_state_t safe_state = helmet_actuator_for_risk(HELMET_RISK_NORMAL);
    return helmet_actuator_apply(&safe_state);
}
