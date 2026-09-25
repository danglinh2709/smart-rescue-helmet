using SmartRescueHelmet.Unity.Environment;
using SmartRescueHelmet.Unity.Contracts;
using SmartRescueHelmet.Unity.Networking;
using UnityEngine;
using System.Threading;

namespace SmartRescueHelmet.Unity.Devices
{
    public sealed class HelmetDeviceController : MonoBehaviour
    {
        public VirtualActuatorController Actuators;
        public MqttDevicePublisher Publisher;
        public string DeviceId = "FF03";
        private float _telemetryAt, _statusAt, _healthAt;
        public HazardVolume[] Hazards;
        public VentilationZone[] VentilationZones;
        public DeviceSensorSnapshot Current { get; } = new DeviceSensorSnapshot { Temperature = 31f, Co = 5f, Az = 9.81f, Battery = 85f };
        public LocalSafetyResult Safety { get; private set; } = new LocalSafetyResult();
        public string EnvironmentDiagnostic { get; private set; } = "ZONE: SAFE";

        private void Update()
        {
            RefreshEnvironmentSensors();
            if (Publisher == null || !Publisher.IsConnected) return;
            if (Time.time >= _telemetryAt) { _telemetryAt = Time.time + 1f; Publish("telemetry", HelmetMessages.CreateTelemetry(DeviceId, Current, Safety), 0); }
            if (Time.time >= _statusAt) { _statusAt = Time.time + 2f; Publish("status", HelmetMessages.CreateStatus(DeviceId, Current, Safety), 1); }
            if (Time.time >= _healthAt) { _healthAt = Time.time + 5f; Publish("health", HelmetMessages.CreateHealth(DeviceId, Current.Battery), 1); }
        }

        public void RefreshEnvironmentSensors()
        {
            var temperature = 31f; var co = 5f;
            var activeZones = new System.Collections.Generic.List<string>();
            foreach (var hazard in Hazards ?? System.Array.Empty<HazardVolume>())
                if (hazard != null && hazard.Contains(transform.position))
                {
                    temperature += hazard.TemperatureDelta;
                    co += hazard.CoPpm;
                    activeZones.Add(hazard.name);
                }
            foreach (var ventilation in VentilationZones ?? System.Array.Empty<VentilationZone>())
                if (ventilation != null && ventilation.Contains(transform.position))
                {
                    co *= 1f - ventilation.CoReduction;
                    activeZones.Add(ventilation.name);
                }
            EnvironmentDiagnostic = $"POS: {transform.position.x:F1}, {transform.position.y:F1}, {transform.position.z:F1} | " +
                (activeZones.Count == 0 ? "ZONE: SAFE" : "ZONE: " + string.Join(", ", activeZones));
            Current.Temperature = temperature; Current.Co = co;
            Safety = LocalSafetyEvaluator.Evaluate(Current);
            if (Actuators != null) Actuators.Apply(Safety);
        }
        private void Publish(string kind, string json, int qos)
        {
            if (JsonContractValidator.IsValid(kind + ".schema.json", json))
                _ = Publisher.PublishAsync(HelmetTopicBuilder.Build(DeviceId, kind), json, qos, CancellationToken.None);
        }
        public void ReportFall() { Current.Fall = true; }
        public void SetSos(bool enabled) { Current.Sos = enabled; }
    }
}
