using SmartRescueHelmet.Unity.Devices;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Scenarios
{
    public enum ScenarioKind { Normal, TemperatureHigh, CoHigh, Fall, Sos, LowBattery, ConnectionLoss, Reconnect }
    public sealed class ScenarioController : MonoBehaviour
    {
        public HelmetDeviceController Helmet;
        public Vector3 NormalSpawn;
        public Vector3 TemperatureTarget;
        public Vector3 CoTarget;
        public Vector3 FallTarget;
        public ScenarioKind ActiveScenario { get; private set; } = ScenarioKind.Normal;
        public void Activate(ScenarioKind scenario)
        {
            if (Helmet == null) return;
            ActiveScenario = scenario;
            Helmet.Current.Fall = false; Helmet.Current.Sos = false; Helmet.Current.Battery = 85f;
            switch (scenario)
            {
                case ScenarioKind.Normal:
                    Helmet.transform.position = NormalSpawn;
                    if (Helmet.Publisher != null) Helmet.Publisher.SetPublishingEnabled(true);
                    break;
                case ScenarioKind.TemperatureHigh: Helmet.transform.position = TemperatureTarget; break;
                case ScenarioKind.CoHigh: Helmet.transform.position = CoTarget; break;
                case ScenarioKind.Fall:
                    Helmet.transform.position = FallTarget;
                    Helmet.ReportFall();
                    break;
                case ScenarioKind.Sos: Helmet.SetSos(true); break;
                case ScenarioKind.LowBattery: Helmet.Current.Battery = 15f; break;
                case ScenarioKind.ConnectionLoss: if (Helmet.Publisher != null) Helmet.Publisher.SetPublishingEnabled(false); break;
                case ScenarioKind.Reconnect: if (Helmet.Publisher != null) Helmet.Publisher.SetPublishingEnabled(true); break;
            }
        }
        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.Alpha1)) Activate(ScenarioKind.Normal);
            if (Input.GetKeyDown(KeyCode.Alpha2)) Activate(ScenarioKind.Fall);
            if (Input.GetKeyDown(KeyCode.Alpha3)) Activate(ScenarioKind.Sos);
            if (Input.GetKeyDown(KeyCode.Alpha4)) Activate(ScenarioKind.LowBattery);
            if (Input.GetKeyDown(KeyCode.Alpha5)) Activate(ScenarioKind.ConnectionLoss);
            if (Input.GetKeyDown(KeyCode.Alpha6)) Activate(ScenarioKind.Reconnect);
            if (Input.GetKeyDown(KeyCode.Alpha7)) Activate(ScenarioKind.TemperatureHigh);
            if (Input.GetKeyDown(KeyCode.Alpha8)) Activate(ScenarioKind.CoHigh);
        }
    }
}
