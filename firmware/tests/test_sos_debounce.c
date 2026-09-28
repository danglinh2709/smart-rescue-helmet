#include <assert.h>

#include "sos.h"

int main(void)
{
    helmet_sos_debouncer_t state = helmet_sos_debouncer_initial();
    assert(!helmet_sos_debouncer_update(&state, true, 0));
    assert(!helmet_sos_debouncer_update(&state, false, 10));
    assert(!helmet_sos_debouncer_update(&state, false, 39));
    assert(helmet_sos_debouncer_update(&state, false, 40));
    return 0;
}
