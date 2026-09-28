idf_component_register(
  SRCS "app_main.c" "safety_engine.c" "actuator_controller.c" "mqtt_contract.c" "time_sync.c" "connectivity.c" "sensor_manager.c" "sos.c" "sos_driver.c" "i2c_bus.c" "i2c_runtime.c" "mpu6050.c" "ads1115.c" "ds18b20_sensor.c" "battery.c"
    INCLUDE_DIRS "include"
  REQUIRES esp_adc esp_driver_gpio esp_driver_i2c esp_driver_rmt esp_wifi esp_event esp_netif
)
