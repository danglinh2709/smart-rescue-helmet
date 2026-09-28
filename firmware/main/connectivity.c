#include "connectivity.h"
#include "connectivity_runtime.h"

#include <string.h>

#include "esp_event.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_netif.h"
#include "esp_netif_sntp.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "mqtt_client.h"

static const char *TAG = "helmet_connectivity";
static esp_mqtt_client_handle_t mqtt_client;
static bool wifi_connected;
static bool mqtt_connected;
static bool sntp_started;
static uint8_t wifi_retry_attempt;
static esp_timer_handle_t wifi_retry_timer;

bool helmet_connectivity_publish_ready(bool wifi_ready, bool mqtt_ready, bool time_ready)
{
    return wifi_ready && mqtt_ready && time_ready;
}

uint32_t helmet_connectivity_retry_delay_ms(uint8_t attempt)
{
    return attempt >= 5 ? 30000U : 1000U << attempt;
}

static void wifi_retry_callback(void *argument)
{
    (void)argument;
    ESP_LOGI(TAG, "Wi-Fi reconnect attempt");
    esp_err_t result = esp_wifi_connect();
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "Wi-Fi reconnect call failed: %s", esp_err_to_name(result));
    }
}

static void schedule_wifi_reconnect(void)
{
    const uint32_t delay_ms = helmet_connectivity_retry_delay_ms(wifi_retry_attempt);
    if (wifi_retry_attempt < 5) {
        ++wifi_retry_attempt;
    }
    (void)esp_timer_stop(wifi_retry_timer);
    ESP_ERROR_CHECK(esp_timer_start_once(wifi_retry_timer, (uint64_t)delay_ms * 1000U));
    ESP_LOGW(TAG, "Wi-Fi disconnected; retry in %lu ms", (unsigned long)delay_ms);
}

static void start_sntp_once(void)
{
    if (sntp_started) {
        return;
    }
    const esp_sntp_config_t config = ESP_NETIF_SNTP_DEFAULT_CONFIG("pool.ntp.org");
    ESP_ERROR_CHECK(esp_netif_sntp_init(&config));
    sntp_started = true;
    ESP_LOGI(TAG, "SNTP started after Wi-Fi IP acquisition");
}

static void mqtt_event_handler(void *argument, esp_event_base_t base,
    int32_t event_id, void *event_data)
{
    (void)argument;
    (void)base;
    (void)event_data;
    if (event_id == MQTT_EVENT_CONNECTED) {
        mqtt_connected = true;
        ESP_LOGI(TAG, "MQTT connected");
    } else if (event_id == MQTT_EVENT_DISCONNECTED) {
        mqtt_connected = false;
        ESP_LOGW(TAG, "MQTT disconnected; client retry is active");
    }
}

static void wifi_event_handler(void *argument, esp_event_base_t base,
    int32_t event_id, void *event_data)
{
    (void)argument;
    (void)event_data;
    if (base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        ESP_ERROR_CHECK(esp_wifi_connect());
    } else if (base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        wifi_connected = false;
        mqtt_connected = false;
        schedule_wifi_reconnect();
    } else if (base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        wifi_connected = true;
        wifi_retry_attempt = 0;
        (void)esp_timer_stop(wifi_retry_timer);
        start_sntp_once();
        ESP_LOGI(TAG, "Wi-Fi connected with IP address");
    }
}

esp_err_t helmet_connectivity_start(void)
{
    ESP_RETURN_ON_ERROR(esp_netif_init(), TAG, "netif init failed");
    ESP_RETURN_ON_ERROR(esp_event_loop_create_default(), TAG, "event loop failed");
    esp_netif_create_default_wifi_sta();

    const wifi_init_config_t wifi_init = WIFI_INIT_CONFIG_DEFAULT();
    ESP_RETURN_ON_ERROR(esp_wifi_init(&wifi_init), TAG, "Wi-Fi init failed");
    const esp_timer_create_args_t retry_timer_config = {
        .callback = wifi_retry_callback,
        .name = "helmet_wifi_retry",
    };
    ESP_RETURN_ON_ERROR(esp_timer_create(&retry_timer_config, &wifi_retry_timer), TAG,
        "Wi-Fi retry timer failed");
    ESP_RETURN_ON_ERROR(esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID,
        &wifi_event_handler, NULL, NULL), TAG, "Wi-Fi handler failed");
    ESP_RETURN_ON_ERROR(esp_event_handler_instance_register(IP_EVENT, IP_EVENT_STA_GOT_IP,
        &wifi_event_handler, NULL, NULL), TAG, "IP handler failed");

    wifi_config_t wifi_config = { 0 };
    strlcpy((char *)wifi_config.sta.ssid, CONFIG_HELMET_WIFI_SSID,
        sizeof(wifi_config.sta.ssid));
    strlcpy((char *)wifi_config.sta.password, CONFIG_HELMET_WIFI_PASSWORD,
        sizeof(wifi_config.sta.password));
    wifi_config.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;
    ESP_RETURN_ON_ERROR(esp_wifi_set_mode(WIFI_MODE_STA), TAG, "Wi-Fi mode failed");
    ESP_RETURN_ON_ERROR(esp_wifi_set_config(WIFI_IF_STA, &wifi_config), TAG,
        "Wi-Fi configuration failed");
    ESP_RETURN_ON_ERROR(esp_wifi_start(), TAG, "Wi-Fi start failed");

    const esp_mqtt_client_config_t mqtt_config = {
        .broker.address.uri = CONFIG_HELMET_MQTT_URI,
        .credentials.username = CONFIG_HELMET_MQTT_USERNAME,
        .credentials.authentication.password = CONFIG_HELMET_MQTT_PASSWORD,
    };
    mqtt_client = esp_mqtt_client_init(&mqtt_config);
    if (mqtt_client == NULL) {
        return ESP_FAIL;
    }
    ESP_RETURN_ON_ERROR(esp_mqtt_client_register_event(mqtt_client, ESP_EVENT_ANY_ID,
        mqtt_event_handler, NULL), TAG, "MQTT handler failed");
    return esp_mqtt_client_start(mqtt_client);
}

bool helmet_connectivity_wifi_connected(void)
{
    return wifi_connected;
}

bool helmet_connectivity_mqtt_connected(void)
{
    return mqtt_connected;
}

esp_err_t helmet_connectivity_publish(const char *topic, const char *payload, int qos)
{
    if (mqtt_client == NULL || !mqtt_connected || topic == NULL || payload == NULL) {
        return ESP_ERR_INVALID_STATE;
    }
    return esp_mqtt_client_publish(mqtt_client, topic, payload, 0, qos, 0) >= 0
        ? ESP_OK : ESP_FAIL;
}
