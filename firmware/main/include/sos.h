#pragma once

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    bool stable_pressed;
    bool candidate_pressed;
    uint32_t candidate_since_ms;
} helmet_sos_debouncer_t;

helmet_sos_debouncer_t helmet_sos_debouncer_initial(void);
bool helmet_sos_debouncer_update(helmet_sos_debouncer_t *state,
    bool pin_high, uint32_t now_ms);
