#include <assert.h>

#include "mpu6050.h"

int main(void)
{
    assert(helmet_mpu6050_identity_valid(0x68));
    assert(!helmet_mpu6050_identity_valid(0x00));
    assert(!helmet_mpu6050_identity_valid(0xff));
    return 0;
}
