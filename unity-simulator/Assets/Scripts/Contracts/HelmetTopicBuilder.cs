using System;
using System.Text.RegularExpressions;

namespace SmartRescueHelmet.Unity.Contracts
{
    public static class HelmetTopicBuilder
    {
        private static readonly Regex DeviceIdPattern =
            new Regex("^[A-Z][A-Z0-9_-]{2,31}$", RegexOptions.Compiled);

        public static string Build(string deviceId, string messageType)
        {
            if (string.IsNullOrWhiteSpace(deviceId) || !DeviceIdPattern.IsMatch(deviceId))
            {
                throw new ArgumentException("device_id must match the shared contract.", nameof(deviceId));
            }

            switch (messageType)
            {
                case "telemetry":
                case "event":
                case "status":
                case "health":
                    return "helmet/" + deviceId + "/" + messageType;
                default:
                    throw new ArgumentException("Unsupported MQTT message type.", nameof(messageType));
            }
        }
    }
}
