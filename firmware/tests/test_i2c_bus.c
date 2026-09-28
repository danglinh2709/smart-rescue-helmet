#include <assert.h>

#include "i2c_bus.h"

int main(void)
{
    assert(helmet_i2c_is_mpu6050_address(0x68));
    assert(helmet_i2c_is_mpu6050_address(0x69));
    assert(!helmet_i2c_is_mpu6050_address(0x67));
    assert(helmet_i2c_is_ads1115_address(0x48));
    assert(helmet_i2c_is_ads1115_address(0x4b));
    assert(!helmet_i2c_is_ads1115_address(0x4c));
    return 0;
}
