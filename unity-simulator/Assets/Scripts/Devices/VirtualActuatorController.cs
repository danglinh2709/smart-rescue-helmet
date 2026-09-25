using UnityEngine;

namespace SmartRescueHelmet.Unity.Devices
{
    public sealed class VirtualActuatorController : MonoBehaviour
    {
        public Renderer LedRenderer;
        public Renderer BuzzerIndicator;
        public Renderer VibrationIndicator;
        public bool BuzzerOn { get; private set; }
        public bool VibrationOn { get; private set; }
        public string Led { get; private set; } = "GREEN";

        public void Apply(LocalSafetyResult safety)
        {
            Led = safety.RiskLevel == "CRITICAL" ? "RED" : safety.RiskLevel == "WARNING" ? "YELLOW" : "GREEN";
            BuzzerOn = safety.RiskLevel == "CRITICAL";
            VibrationOn = BuzzerOn;
            if (LedRenderer != null) LedRenderer.material.color = Led == "RED" ? Color.red : Led == "YELLOW" ? Color.yellow : Color.green;
            SetIndicator(BuzzerIndicator, BuzzerOn);
            SetIndicator(VibrationIndicator, VibrationOn);
        }

        private static void SetIndicator(Renderer indicator, bool active)
        {
            if (indicator != null) indicator.material.color = active ? Color.red : new Color(.12f, .12f, .12f);
        }
    }
}
