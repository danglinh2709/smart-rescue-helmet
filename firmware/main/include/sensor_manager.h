#pragma once

#include "esp_err.h"
#include "helmet_types.h"

/** Creates the safe startup snapshot used until physical drivers report data. */
helmet_sensor_snapshot_t helmet_sensor_snapshot_unavailable(void);

/** Initializes local inputs. Missing optional I2C sensors remain unavailable. */
esp_err_t helmet_sensor_manager_init(void);

/** Returns the latest physical readings without inventing values for unavailable sensors. */
helmet_sensor_snapshot_t helmet_sensor_manager_read(void);
