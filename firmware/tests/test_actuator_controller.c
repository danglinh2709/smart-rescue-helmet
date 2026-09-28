#include <assert.h>

#include "actuator_controller.h"

int main(void)
{
    helmet_actuator_state_t normal = helmet_actuator_for_risk(HELMET_RISK_NORMAL);
    assert(normal.led_green && !normal.led_yellow && !normal.led_red);
    assert(!normal.buzzer_on && !normal.vibration_on);

    helmet_actuator_state_t warning = helmet_actuator_for_risk(HELMET_RISK_WARNING);
    assert(!warning.led_green && warning.led_yellow && !warning.led_red);
    assert(!warning.buzzer_on && !warning.vibration_on);

    helmet_actuator_state_t critical = helmet_actuator_for_risk(HELMET_RISK_CRITICAL);
    assert(!critical.led_green && !critical.led_yellow && critical.led_red);
    assert(critical.buzzer_on && critical.vibration_on);
    return 0;
}
