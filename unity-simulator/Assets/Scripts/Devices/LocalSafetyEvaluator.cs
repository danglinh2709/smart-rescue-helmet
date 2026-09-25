namespace SmartRescueHelmet.Unity.Devices
{
    public sealed class LocalSafetyResult
    {
        public string RiskLevel = "NORMAL";
    }

    public static class LocalSafetyEvaluator
    {
        public static LocalSafetyResult Evaluate(DeviceSensorSnapshot value)
        {
            var critical = value.Temperature >= 60f || value.Co >= 100f || value.Battery <= 20f || value.Fall || value.Sos;
            var warning = value.Temperature >= 50f || value.Co >= 50f;
            return new LocalSafetyResult { RiskLevel = critical ? "CRITICAL" : warning ? "WARNING" : "NORMAL" };
        }
    }
}
