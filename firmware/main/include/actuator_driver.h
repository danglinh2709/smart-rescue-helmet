#pragma once

#include "esp_err.h"
#include "helmet_types.h"

/** Initializes output GPIO and applies the non-alarming NORMAL state. */
esp_err_t helmet_actuator_init(void);

/** Applies a previously evaluated state. It never evaluates sensor data. */
esp_err_t helmet_actuator_apply(const helmet_actuator_state_t *state);
