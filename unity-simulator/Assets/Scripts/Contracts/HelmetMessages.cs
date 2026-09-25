using System;
using System.Collections.Generic;
using System.Text.Json;
using SmartRescueHelmet.Unity.Devices;

namespace SmartRescueHelmet.Unity.Contracts
{
    public static class HelmetMessages
    {
        public static string CreateStatus(string deviceId, string risk) =>
            $"{{\"schema_version\":\"1.0\",\"device_id\":\"{deviceId}\",\"timestamp\":\"{DateTimeOffset.UtcNow:O}\",\"source\":\"SIMULATOR\",\"device_status\":\"ONLINE\",\"risk_level\":\"{risk}\",\"movement\":\"WALKING\",\"fall\":false,\"immobile\":false,\"sos\":false}}";

        public static string CreateStatus(
            string deviceId,
            DeviceSensorSnapshot snapshot,
            LocalSafetyResult safety)
        {
            return JsonSerializer.Serialize(new Dictionary<string, object>
            {
                ["schema_version"] = "1.0",
                ["device_id"] = deviceId,
                ["timestamp"] = DateTimeOffset.UtcNow.ToString("O"),
                ["source"] = "SIMULATOR",
                ["device_status"] = "ONLINE",
                ["risk_level"] = safety.RiskLevel,
                ["movement"] = snapshot.Movement,
                ["fall"] = snapshot.Fall,
                ["immobile"] = snapshot.Immobile,
                ["sos"] = snapshot.Sos,
            });
        }
        public static string CreateHealth(string deviceId, float battery) =>
            $"{{\"schema_version\":\"1.0\",\"device_id\":\"{deviceId}\",\"timestamp\":\"{DateTimeOffset.UtcNow:O}\",\"source\":\"SIMULATOR\",\"battery\":{battery.ToString(System.Globalization.CultureInfo.InvariantCulture)},\"uptime_seconds\":1,\"wifi\":\"CONNECTED\",\"mqtt\":\"CONNECTED\",\"sensors\":{{\"temperature\":\"OK\",\"co\":\"OK\",\"imu\":\"OK\"}}}}";
        public static string CreateNormalTelemetry(string deviceId)
        {
            return CreateTelemetry(
                deviceId,
                new DeviceSensorSnapshot { Temperature = 31f, Co = 5f, Az = 9.81f, Battery = 85f },
                new LocalSafetyResult { RiskLevel = "NORMAL" });
        }

        public static string CreateTelemetry(
            string deviceId,
            DeviceSensorSnapshot snapshot,
            LocalSafetyResult safety)
        {
            var message = new Dictionary<string, object>
            {
                ["schema_version"] = "1.0",
                ["device_id"] = deviceId,
                ["timestamp"] = DateTimeOffset.UtcNow.ToString("O"),
                ["source"] = "SIMULATOR",
                ["sensors"] = new Dictionary<string, object>
                {
                    ["temperature"] = snapshot.Temperature,
                    ["co"] = snapshot.Co,
                    ["imu"] = new Dictionary<string, double>
                    {
                        ["ax"] = snapshot.Ax, ["ay"] = snapshot.Ay, ["az"] = snapshot.Az,
                        ["gx"] = snapshot.Gx, ["gy"] = snapshot.Gy, ["gz"] = snapshot.Gz
                    }
                },
                ["state"] = new Dictionary<string, object>
                {
                    ["movement"] = snapshot.Movement, ["fall"] = snapshot.Fall,
                    ["immobile"] = snapshot.Immobile, ["sos"] = snapshot.Sos
                },
                ["risk_level"] = safety.RiskLevel,
                ["device"] = new Dictionary<string, object>
                {
                    ["battery"] = snapshot.Battery, ["wifi"] = snapshot.Wifi, ["mqtt"] = snapshot.Mqtt
                }
            };

            return JsonSerializer.Serialize(message);
        }
    }
}
