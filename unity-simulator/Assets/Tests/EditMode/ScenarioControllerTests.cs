using NUnit.Framework;
using SmartRescueHelmet.Unity.Devices;
using SmartRescueHelmet.Unity.Scenarios;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Tests.EditMode
{
    public sealed class ScenarioControllerTests
    {
        [Test]
        public void Temperature_high_scenario_moves_the_helmet_to_the_heat_target()
        {
            var helmetObject = new GameObject("Helmet");
            var controllerObject = new GameObject("ScenarioController");
            try
            {
                var helmet = helmetObject.AddComponent<HelmetDeviceController>();
                var scenarios = controllerObject.AddComponent<ScenarioController>();
                scenarios.Helmet = helmet;
                scenarios.TemperatureTarget = new Vector3(4f, 1f, 0f);

                scenarios.Activate(ScenarioKind.TemperatureHigh);

                Assert.That(helmet.transform.position, Is.EqualTo(new Vector3(4f, 1f, 0f)));
            }
            finally
            {
                Object.DestroyImmediate(controllerObject);
                Object.DestroyImmediate(helmetObject);
            }
        }
    }
}
