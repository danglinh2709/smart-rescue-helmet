using SmartRescueHelmet.Unity.Devices;
using SmartRescueHelmet.Unity.Scenarios;
using SmartRescueHelmet.Unity.Networking;
using SmartRescueHelmet.Unity.Player;
using SmartRescueHelmet.Unity.Rescue;
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
        public RescueMission Mission;
        public RescuerController Rescuer;
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
            GUI.Label(new Rect(32, 172, 430, 24), Device.EnvironmentDiagnostic);
            GUI.Box(new Rect(18, 196, 300, 96), GUIContent.none);
            if (Scenarios != null) GUI.Label(new Rect(32, 196, 250, 24), "SCENARIO: " + Scenarios.ActiveScenario);
            if (Publisher != null) GUI.Label(new Rect(32, 220, 250, 24), "PUBLISH: " + (Publisher.PublishEnabled ? "ENABLED" : "DISABLED"));
            if (BackendRealtime != null)
            {
                GUI.Label(new Rect(32, 244, 270, 24), "BACKEND WS: " + (BackendRealtime.IsConnected ? "CONNECTED" : "RECONNECTING"));
                GUI.Label(new Rect(32, 268, 270, 24), "WS MESSAGE: " + BackendRealtime.LastMessageType);
                var backend = BackendRealtime.State;
                GUI.Label(new Rect(Screen.width - 260, 48, 240, 24), "BACKEND RISK: " + backend.RiskLevel);
                GUI.Label(new Rect(Screen.width - 260, 72, 240, 24), "BACKEND TEMP: " + (backend.Temperature.HasValue ? backend.Temperature.Value.ToString("F1") + " C" : "--"));
                GUI.Label(new Rect(Screen.width - 260, 96, 240, 24), "BACKEND CO: " + (backend.Co.HasValue ? backend.Co.Value.ToString("F1") + " ppm" : "--"));
                GUI.Label(new Rect(Screen.width - 260, 120, 240, 24), "BACKEND BATTERY: " + (backend.Battery.HasValue ? backend.Battery.Value.ToString("F0") + "%" : "--"));
            }
            if (Device.Actuators != null)
                GUI.Label(new Rect(32, 292, 250, 24), "ACTUATOR: " + Device.Actuators.Led + " | B:" + (Device.Actuators.BuzzerOn ? "ON" : "OFF") + " V:" + (Device.Actuators.VibrationOn ? "ON" : "OFF"));
            if (Mission != null)
            {
                GUI.Box(new Rect(Screen.width - 330, 220, 300, 94), "RESCUE MISSION");
                GUI.Label(new Rect(Screen.width - 314, 252, 270, 22), "EVACUATED: " + Mission.EvacuatedCount + " / " + Mission.TotalVictims);
                GUI.Label(new Rect(Screen.width - 314, 274, 270, 22), "TIME REMAINING: " + Mathf.CeilToInt(Mission.RemainingSeconds) + " s");
                if (Mission.IsFailed)
                    GUI.Label(new Rect(Screen.width - 314, 296, 270, 22), "MISSION FAILED - TIME EXPIRED");
                else if (Mission.IsComplete)
                    GUI.Label(new Rect(Screen.width - 314, 276, 270, 22), "MISSION COMPLETE - ALL SAFE");
                else if (Rescuer != null && Rescuer.NearbyVictim != null)
                    GUI.Label(new Rect(Screen.width - 314, 296, 270, 22), "PRESS F TO ASSIST " + Rescuer.NearbyVictim.name);
                else
                    GUI.Label(new Rect(Screen.width - 314, 296, 270, 22), "FIND A VICTIM - GREEN AREA IS SAFE ZONE");
            }
            GUI.Box(new Rect(18, Screen.height - 90, 410, 72), "CONTROLS");
            GUI.Label(new Rect(32, Screen.height - 64, 380, 22), "WASD move | Q/E or arrows turn | C camera");
            GUI.Label(new Rect(32, Screen.height - 40, 700, 22), "F assist victim | 1 normal | 2 fall | 3 SOS | 4 battery | 5 loss | 6 reconnect | 7 heat | 8 CO | F1 fire | F2 CO scene");
        }
    }
}
