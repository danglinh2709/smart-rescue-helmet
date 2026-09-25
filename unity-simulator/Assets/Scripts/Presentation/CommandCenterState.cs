using System.Text.Json;
using SmartRescueHelmet.Unity.Networking;

namespace SmartRescueHelmet.Unity.Presentation
{
    /// <summary>
    /// Read-only projection of backend WebSocket messages for the Unity
    /// command-center view. It never evaluates risk or device offline state.
    /// </summary>
    public sealed class CommandCenterState
    {
        public string DeviceId { get; private set; } = string.Empty;
        public string LastMessageType { get; private set; } = "NONE";
        public string LastTimestamp { get; private set; } = string.Empty;
        public string DeviceStatus { get; private set; } = "UNKNOWN";
        public string RiskLevel { get; private set; } = "UNKNOWN";
        public string Movement { get; private set; } = "UNKNOWN";
        public string Wifi { get; private set; } = "UNKNOWN";
        public string Mqtt { get; private set; } = "UNKNOWN";
        public string EventType { get; private set; } = string.Empty;
        public string Severity { get; private set; } = string.Empty;
        public string Led { get; private set; } = string.Empty;
        public bool? Buzzer { get; private set; }
        public bool? Vibration { get; private set; }
        public float? Temperature { get; private set; }
        public float? Co { get; private set; }
        public float? Battery { get; private set; }

        public void Apply(RealtimeEnvelope envelope)
        {
            LastMessageType = envelope.MessageType;
            if (!string.IsNullOrEmpty(envelope.DeviceId)) DeviceId = envelope.DeviceId;
            if (!string.IsNullOrEmpty(envelope.Timestamp)) LastTimestamp = envelope.Timestamp;

            using var document = JsonDocument.Parse(envelope.DataJson);
            var data = document.RootElement;
            if (envelope.MessageType == "initial_state")
            {
                if (data.ValueKind == JsonValueKind.Array && data.GetArrayLength() > 0)
                    ApplyDeviceState(data[0]);
                return;
            }

            switch (envelope.MessageType)
            {
                case "telemetry": ApplyTelemetry(data); break;
                case "status": ApplyStatus(data); break;
                case "health": ApplyHealth(data); break;
                case "event": ApplyEvent(data); break;
                case "device_state": ApplyDeviceState(data); break;
            }
        }

        private void ApplyDeviceState(JsonElement data)
        {
            DeviceId = ReadString(data, "device_id", DeviceId);
            DeviceStatus = ReadString(data, "device_status", DeviceStatus);
            RiskLevel = ReadString(data, "risk_level", RiskLevel);
            Movement = ReadString(data, "movement", Movement);
            if (data.TryGetProperty("latest_telemetry", out var telemetry) && telemetry.ValueKind == JsonValueKind.Object)
                ApplyTelemetry(telemetry);
            if (data.TryGetProperty("latest_health", out var health) && health.ValueKind == JsonValueKind.Object)
                ApplyHealth(health);
            if (data.TryGetProperty("latest_event", out var latestEvent) && latestEvent.ValueKind == JsonValueKind.Object)
                ApplyEvent(latestEvent);
            if (data.TryGetProperty("actuators", out var actuators) && actuators.ValueKind == JsonValueKind.Object)
            {
                Led = ReadString(actuators, "led", Led);
                Buzzer = ReadBool(actuators, "buzzer", Buzzer);
                Vibration = ReadBool(actuators, "vibration", Vibration);
            }
        }

        private void ApplyTelemetry(JsonElement data)
        {
            RiskLevel = ReadString(data, "risk_level", RiskLevel);
            if (data.TryGetProperty("sensors", out var sensors) && sensors.ValueKind == JsonValueKind.Object)
            {
                Temperature = ReadNumber(sensors, "temperature", Temperature);
                Co = ReadNumber(sensors, "co", Co);
            }
            if (data.TryGetProperty("state", out var state) && state.ValueKind == JsonValueKind.Object)
                Movement = ReadString(state, "movement", Movement);
            if (data.TryGetProperty("device", out var device) && device.ValueKind == JsonValueKind.Object)
            {
                Battery = ReadNumber(device, "battery", Battery);
                Wifi = ReadString(device, "wifi", Wifi);
                Mqtt = ReadString(device, "mqtt", Mqtt);
            }
        }

        private void ApplyStatus(JsonElement data)
        {
            DeviceStatus = ReadString(data, "device_status", DeviceStatus);
            RiskLevel = ReadString(data, "risk_level", RiskLevel);
            Movement = ReadString(data, "movement", Movement);
        }

        private void ApplyHealth(JsonElement data)
        {
            Battery = ReadNumber(data, "battery", Battery);
            Wifi = ReadString(data, "wifi", Wifi);
            Mqtt = ReadString(data, "mqtt", Mqtt);
        }

        private void ApplyEvent(JsonElement data)
        {
            EventType = ReadString(data, "event_type", EventType);
            Severity = ReadString(data, "severity", Severity);
        }

        private static string ReadString(JsonElement parent, string name, string fallback)
        {
            return parent.TryGetProperty(name, out var value) && value.ValueKind == JsonValueKind.String
                ? value.GetString()
                : fallback;
        }

        private static float? ReadNumber(JsonElement parent, string name, float? fallback)
        {
            return parent.TryGetProperty(name, out var value) && value.TryGetSingle(out var result)
                ? result
                : fallback;
        }

        private static bool? ReadBool(JsonElement parent, string name, bool? fallback)
        {
            return parent.TryGetProperty(name, out var value) &&
                   (value.ValueKind == JsonValueKind.True || value.ValueKind == JsonValueKind.False)
                ? value.GetBoolean()
                : fallback;
        }
    }
}
