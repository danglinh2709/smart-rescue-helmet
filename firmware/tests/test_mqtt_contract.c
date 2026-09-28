#include <assert.h>
#include <string.h>

#include "mqtt_contract.h"

int main(void)
{
    char topic[64];
    assert(helmet_build_topic(topic, sizeof(topic), "FF01", "telemetry"));
    assert(strcmp(topic, "helmet/FF01/telemetry") == 0);
    assert(!helmet_build_topic(topic, sizeof(topic), "ff01", "telemetry"));
    assert(!helmet_build_topic(topic, sizeof(topic), "F1", "telemetry"));
    assert(!helmet_build_topic(topic, sizeof(topic), "FF 01", "telemetry"));
    assert(!helmet_build_topic(topic, 8, "FF01", "telemetry"));
    return 0;
}
