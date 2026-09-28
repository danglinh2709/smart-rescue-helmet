#include "battery.h"

#include "esp_adc/adc_cali_scheme.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_check.h"
#include "helmet_config.h"
#include "sdkconfig.h"

static adc_oneshot_unit_handle_t adc_handle;
static adc_cali_handle_t calibration_handle;
static adc_channel_t adc_channel;

float helmet_battery_percent_from_pack_mv(int pack_mv, int empty_mv, int full_mv)
{
    if (full_mv <= empty_mv || pack_mv <= empty_mv) {
        return 0.0f;
    }
    if (pack_mv >= full_mv) {
        return 100.0f;
    }
    return ((float)(pack_mv - empty_mv) * 100.0f) / (float)(full_mv - empty_mv);
}

esp_err_t helmet_battery_init(void)
{
    if (adc_handle != NULL && calibration_handle != NULL) {
        return ESP_OK;
    }
    adc_unit_t unit;
    ESP_RETURN_ON_ERROR(adc_oneshot_io_to_channel(HELMET_PIN_BATTERY_ADC, &unit, &adc_channel),
        "battery", "GPIO is not ADC capable");
    if (unit != ADC_UNIT_1) {
        return ESP_ERR_NOT_SUPPORTED;
    }
    const adc_oneshot_unit_init_cfg_t unit_config = { .unit_id = unit };
    ESP_RETURN_ON_ERROR(adc_oneshot_new_unit(&unit_config, &adc_handle), "battery", "ADC init");
    const adc_oneshot_chan_cfg_t channel_config = {
        .atten = ADC_ATTEN_DB_12,
        .bitwidth = ADC_BITWIDTH_DEFAULT,
    };
    ESP_RETURN_ON_ERROR(adc_oneshot_config_channel(adc_handle, adc_channel, &channel_config),
        "battery", "ADC channel config");
#if ADC_CALI_SCHEME_CURVE_FITTING_SUPPORTED
    const adc_cali_curve_fitting_config_t calibration_config = {
        .unit_id = unit,
        .chan = adc_channel,
        .atten = ADC_ATTEN_DB_12,
        .bitwidth = ADC_BITWIDTH_DEFAULT,
    };
    return adc_cali_create_scheme_curve_fitting(&calibration_config, &calibration_handle);
#else
    return ESP_ERR_NOT_SUPPORTED;
#endif
}

esp_err_t helmet_battery_read_percent(float *percent)
{
    if (percent == NULL || adc_handle == NULL || calibration_handle == NULL) {
        return ESP_ERR_INVALID_STATE;
    }
    int pin_mv = 0;
    ESP_RETURN_ON_ERROR(adc_oneshot_get_calibrated_result(adc_handle, calibration_handle,
        adc_channel, &pin_mv), "battery", "calibrated ADC read");
    const int pack_mv = (pin_mv * CONFIG_HELMET_BATTERY_DIVIDER_MILLI_GAIN) / 1000;
    *percent = helmet_battery_percent_from_pack_mv(pack_mv,
        CONFIG_HELMET_BATTERY_EMPTY_MV, CONFIG_HELMET_BATTERY_FULL_MV);
    return ESP_OK;
}
