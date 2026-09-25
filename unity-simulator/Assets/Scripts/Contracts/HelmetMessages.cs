using System;
using System.Collections.Generic;
using System.Text.Json;

namespace SmartRescueHelmet.Unity.Contracts
{
    public static class HelmetMessages
    {
        public static string CreateStatus(string deviceId, string risk) =>
            $"{{\"schema_version\":\"1.0\",\"device_id\":\"{deviceId}\",\"timestamp\":\"{DateTimeOffset.UtcNow:O}\",\"source\":\"SIMULATOR\",\"device_status\":\"ONLINE\",\"risk_level\":\"{risk}\",\"movement\":\"WALKING\",\"fall\":false,\"immobile\":false,\"sos\":false}}";
        public static string CreateHealth(string deviceId, float battery) =>
            $"{{\"schema_version\":\"1.0\",\"device_id\":\"{deviceId}\",\"timestamp\":\"{DateTimeOffset.UtcNow:O}\",\"source\":\"SIMULATOR\",\"battery\":{battery.ToString(System.Globalization.CultureInfo.InvariantCulture)},\"uptime_seconds\":1,\"wifi\":\"CONNECTED\",\"mqtt\":\"CONNECTED\",\"sensors\":{{\"temperature\":\"OK\",\"co\":\"OK\",\"imu\":\"OK\"}}}}";
        public static string CreateNormalTelemetry(string deviceId)
        {
            var message = new Dictionary<string, object>
            {
                ["schema_version"] = "1.0",
                ["device_id"] = deviceId,
                ["timestamp"] = DateTimeOffset.UtcNow.ToString("O"),
                ["source"] = "SIMULATOR",
                ["sensors"] = new Dictionary<string, object>
                {
                    ["temperature"] = 31.0,
                    ["co"] = 5.0,
                    ["imu"] = new Dictionary<string, double>
                    {
                        ["ax"] = 0.02, ["ay"] = 0.01, ["az"] = 9.81,
                        ["gx"] = 0.01, ["gy"] = 0.02, ["gz"] = 0.01
                    }
                },
                ["state"] = new Dictionary<string, object>
                {
                    ["movement"] = "WALKING", ["fall"] = false,
                    ["immobile"] = false, ["sos"] = false
                },
                ["risk_level"] = "NORMAL",
                ["device"] = new Dictionary<string, object>
                {
                    ["battery"] = 85.0, ["wifi"] = "CONNECTED", ["mqtt"] = "CONNECTED"
                }
            };

            return JsonSerializer.Serialize(message);
        }
    }
}
