using System;
using System.Text.Json;

namespace SmartRescueHelmet.Unity.Networking
{
    public readonly struct RealtimeEnvelope
    {
        public RealtimeEnvelope(string messageType, string deviceId, string timestamp, string dataJson)
        {
            MessageType = messageType;
            DeviceId = deviceId;
            Timestamp = timestamp;
            DataJson = dataJson;
        }

        public string MessageType { get; }
        public string DeviceId { get; }
        public string Timestamp { get; }
        public string DataJson { get; }
    }

    /// <summary>
    /// Parses the JSON envelope emitted by the backend's /ws endpoint.
    /// The raw data JSON is intentionally preserved so presentation code can
    /// render only the fields it understands without inventing a second contract.
    /// </summary>
    public static class RealtimeEnvelopeParser
    {
        public static bool TryParse(string payload, out RealtimeEnvelope envelope)
        {
            envelope = default;
            if (string.IsNullOrWhiteSpace(payload)) return false;

            try
            {
                using var document = JsonDocument.Parse(payload);
                var root = document.RootElement;
                if (root.ValueKind != JsonValueKind.Object ||
                    !root.TryGetProperty("type", out var typeElement) ||
                    typeElement.ValueKind != JsonValueKind.String)
                    return false;

                var messageType = typeElement.GetString();
                if (!IsSupportedMessageType(messageType)) return false;

                var deviceId = ReadOptionalString(root, "device_id");
                var timestamp = ReadOptionalString(root, "timestamp");
                var dataJson = root.TryGetProperty("data", out var data)
                    ? data.GetRawText()
                    : "null";

                envelope = new RealtimeEnvelope(messageType, deviceId, timestamp, dataJson);
                return true;
            }
            catch (JsonException)
            {
                return false;
            }
        }

        private static string ReadOptionalString(JsonElement root, string propertyName)
        {
            return root.TryGetProperty(propertyName, out var property) &&
                   property.ValueKind == JsonValueKind.String
                ? property.GetString()
                : string.Empty;
        }

        private static bool IsSupportedMessageType(string messageType)
        {
            return messageType == "initial_state" ||
                   messageType == "telemetry" ||
                   messageType == "status" ||
                   messageType == "health" ||
                   messageType == "event" ||
                   messageType == "device_state";
        }
    }
}
