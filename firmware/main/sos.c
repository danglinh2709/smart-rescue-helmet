#include "sos.h"

#include <stddef.h>

#define HELMET_SOS_DEBOUNCE_MS 30U

helmet_sos_debouncer_t helmet_sos_debouncer_initial(void)
{
    return (helmet_sos_debouncer_t){ .stable_pressed = false, .candidate_pressed = false };
}

bool helmet_sos_debouncer_update(helmet_sos_debouncer_t *state,
    bool pin_high, uint32_t now_ms)
{
    if (state == NULL) return false;
    const bool pressed = !pin_high;
    if (pressed != state->candidate_pressed) {
        state->candidate_pressed = pressed;
        state->candidate_since_ms = now_ms;
    }
    if (state->stable_pressed != state->candidate_pressed &&
        now_ms - state->candidate_since_ms >= HELMET_SOS_DEBOUNCE_MS) {
        state->stable_pressed = state->candidate_pressed;
    }
    return state->stable_pressed;
}
