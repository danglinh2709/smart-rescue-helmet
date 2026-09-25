using SmartRescueHelmet.Unity.Devices;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Scenarios
{
    public enum ScenarioKind { Normal, TemperatureHigh, CoHigh, Fall, Sos, LowBattery, ConnectionLoss, Reconnect }
    public sealed class ScenarioController : MonoBehaviour
    {
        public HelmetDeviceController Helmet;
        public void Activate(ScenarioKind scenario)
        {
            if (Helmet == null) return;
            Helmet.Current.Fall = false; Helmet.Current.Sos = false; Helmet.Current.Battery = 85f;
            switch (scenario)
            {
                case ScenarioKind.Fall: Helmet.ReportFall(); break;
                case ScenarioKind.Sos: Helmet.SetSos(true); break;
                case ScenarioKind.LowBattery: Helmet.Current.Battery = 15f; break;
            }
        }
    }
}
