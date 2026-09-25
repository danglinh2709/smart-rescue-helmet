using NUnit.Framework;
using SmartRescueHelmet.Unity.Devices;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Tests.EditMode
{
    public sealed class ActuatorVisualTests
    {
        [Test]
        public void Critical_safety_enables_buzzer_and_vibration_indicators()
        {
            var helmet = new GameObject("Helmet");
            var buzzer = GameObject.CreatePrimitive(PrimitiveType.Cube);
            var vibration = GameObject.CreatePrimitive(PrimitiveType.Cube);
            try
            {
                var actuators = helmet.AddComponent<VirtualActuatorController>();
                actuators.BuzzerIndicator = buzzer.GetComponent<Renderer>();
                actuators.VibrationIndicator = vibration.GetComponent<Renderer>();

                actuators.Apply(new LocalSafetyResult { RiskLevel = "CRITICAL" });

                Assert.That(actuators.BuzzerOn, Is.True);
                Assert.That(actuators.VibrationOn, Is.True);
                Assert.That(actuators.BuzzerIndicator.material.color, Is.EqualTo(Color.red));
                Assert.That(actuators.VibrationIndicator.material.color, Is.EqualTo(Color.red));
            }
            finally
            {
                Object.DestroyImmediate(helmet);
                Object.DestroyImmediate(buzzer);
                Object.DestroyImmediate(vibration);
            }
        }
    }
}
