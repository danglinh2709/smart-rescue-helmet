using SmartRescueHelmet.Unity.Devices;
using SmartRescueHelmet.Unity.Environment;
using SmartRescueHelmet.Unity.Networking;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Bootstrap
{
    public sealed class RuntimeBootstrap : MonoBehaviour
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void CreateAtRuntime()
        {
            if (FindFirstObjectByType<RuntimeBootstrap>() == null)
                new GameObject("RuntimeBootstrap").AddComponent<RuntimeBootstrap>();
        }
        private void Awake()
        {
            Debug.Log("[SRH] RuntimeBootstrap Awake");
            var helmet = new GameObject("RescuerHelmet");
            var actuator = helmet.AddComponent<VirtualActuatorController>();
            var publisher = helmet.AddComponent<MqttDevicePublisher>();
            var device = helmet.AddComponent<HelmetDeviceController>();
            device.Actuators = actuator; device.Publisher = publisher;
            var hazard = GameObject.CreatePrimitive(PrimitiveType.Cube);
            hazard.name = "TemperatureHazard"; hazard.transform.position = new Vector3(4, 0, 0);
            hazard.transform.localScale = new Vector3(3, 3, 3);
            var volume = hazard.AddComponent<HazardVolume>(); volume.TemperatureDelta = 35f;
            device.Hazards = new[] { volume };
        }
    }
}
