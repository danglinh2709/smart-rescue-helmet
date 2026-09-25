using SmartRescueHelmet.Unity.Devices;
using SmartRescueHelmet.Unity.Scenarios;
using SmartRescueHelmet.Unity.Networking;
using SmartRescueHelmet.Unity.Player;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Presentation
{
    public sealed class VisorHudController : MonoBehaviour
    {
        public HelmetDeviceController Device;
        public ScenarioController Scenarios;
        public MqttDevicePublisher Publisher;
        public BackendWebSocketClient BackendRealtime;
        public CameraModeController Cameras;
        private void OnGUI()
        {
            if (Device == null) return;
            GUI.Box(new Rect(18, 18, 280, 180), "SMART RESCUE HELMET — FF03");
            if (Cameras != null) GUI.Label(new Rect(Screen.width - 210, 18, 190, 24), Cameras.IsCommandCenter ? "COMMAND CENTER VIEW" : "HELMET VISOR VIEW");
            GUI.Label(new Rect(32, 52, 250, 24), "TEMPERATURE: " + Device.Current.Temperature.ToString("F1") + " C");
            GUI.Label(new Rect(32, 76, 250, 24), "CO: " + Device.Current.Co.ToString("F1") + " ppm");
            GUI.Label(new Rect(32, 100, 250, 24), "RISK: " + Device.Safety.RiskLevel);
            GUI.Label(new Rect(32, 124, 250, 24), "BATTERY: " + Device.Current.Battery.ToString("F0") + "%");
            GUI.Label(new Rect(32, 148, 250, 24), "MQTT: " + Device.Current.Mqtt);
            if (Scenarios != null) GUI.Label(new Rect(32, 196, 250, 24), "SCENARIO: " + Scenarios.ActiveScenario);
            if (Publisher != null) GUI.Label(new Rect(32, 220, 250, 24), "PUBLISH: " + (Publisher.PublishEnabled ? "ENABLED" : "DISABLED"));
            if (BackendRealtime != null)
            {
                GUI.Label(new Rect(32, 244, 270, 24), "BACKEND WS: " + (BackendRealtime.IsConnected ? "CONNECTED" : "RECONNECTING"));
                GUI.Label(new Rect(32, 268, 270, 24), "WS MESSAGE: " + BackendRealtime.LastMessageType);
            }
            if (Device.Actuators != null)
                GUI.Label(new Rect(32, 172, 250, 24), "ACTUATOR: " + Device.Actuators.Led + " | B:" + (Device.Actuators.BuzzerOn ? "ON" : "OFF") + " V:" + (Device.Actuators.VibrationOn ? "ON" : "OFF"));
            GUI.Box(new Rect(18, Screen.height - 90, 410, 72), "CONTROLS");
            GUI.Label(new Rect(32, Screen.height - 64, 380, 22), "WASD move | Q/E or arrows turn | C camera");
            GUI.Label(new Rect(32, Screen.height - 40, 500, 22), "1 normal | 2 fall | 3 SOS | 4 battery | 5 loss | 6 reconnect");
        }
    }
}
