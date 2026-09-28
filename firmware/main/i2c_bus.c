#include "i2c_bus.h"

bool helmet_i2c_is_mpu6050_address(uint8_t address)
{
    return address == 0x68 || address == 0x69;
}

bool helmet_i2c_is_ads1115_address(uint8_t address)
{
    return address >= 0x48 && address <= 0x4b;
}
