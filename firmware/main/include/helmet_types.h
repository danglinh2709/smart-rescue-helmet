#pragma once

#include <stdbool.h>

typedef enum {
    HELMET_RISK_NORMAL = 0,
    HELMET_RISK_WARNING,
    HELMET_RISK_CRITICAL,
} helmet_risk_level_t;

typedef enum {
    HELMET_MOVEMENT_UNKNOWN = 0,
    HELMET_MOVEMENT_STATIONARY,
    HELMET_MOVEMENT_WALKING,
    HELMET_MOVEMENT_RUNNING,
    HELMET_MOVEMENT_CRAWLING,
    HELMET_MOVEMENT_UNUSUAL_MOVEMENT,
    HELMET_MOVEMENT_FALL,
    HELMET_MOVEMENT_IMMOBILE,
} helmet_movement_state_t;

typedef enum {
    HELMET_CONNECTION_DISCONNECTED = 0,
    HELMET_CONNECTION_CONNECTED,
} helmet_connection_state_t;

typedef enum {
    HELMET_SENSOR_OK = 0,
    HELMET_SENSOR_ERROR,
    HELMET_SENSOR_UNAVAILABLE,
} helmet_sensor_status_t;

typedef struct {
    float ax;
    float ay;
    float az;
    float gx;
    float gy;
    float gz;
} helmet_imu_reading_t;

typedef struct {
    bool temperature_available;
    bool co_available;
    bool battery_available;
    bool imu_available;
    bool fall_detected;
    bool immobile;
    bool sos_pressed;
    float temperature_c;
    float co_ppm;
    float battery_percent;
    helmet_imu_reading_t imu;
    helmet_movement_state_t movement;
} helmet_sensor_snapshot_t;

typedef struct {
    helmet_risk_level_t risk;
    bool temperature_warning;
    bool temperature_critical;
    bool co_warning;
    bool co_critical;
    bool low_battery;
    bool fall_critical;
    bool sos_critical;
} helmet_safety_result_t;

typedef struct {
    bool led_green;
    bool led_yellow;
    bool led_red;
    bool buzzer_on;
    bool vibration_on;
} helmet_actuator_state_t;
