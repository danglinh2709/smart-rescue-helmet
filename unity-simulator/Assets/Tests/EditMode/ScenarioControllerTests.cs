using NUnit.Framework;
using SmartRescueHelmet.Unity.Devices;
using SmartRescueHelmet.Unity.Environment;
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

        [Test]
        public void Temperature_high_scenario_immediately_refreshes_the_sensor_snapshot()
        {
            var helmetObject = new GameObject("Helmet");
            var controllerObject = new GameObject("ScenarioController");
            var heatObject = GameObject.CreatePrimitive(PrimitiveType.Cube);
            try
            {
                heatObject.transform.position = new Vector3(4f, 0f, 0f);
                heatObject.transform.localScale = new Vector3(3f, 3f, 3f);
                var heat = heatObject.AddComponent<HazardVolume>();
                heat.TemperatureDelta = 35f;

                var helmet = helmetObject.AddComponent<HelmetDeviceController>();
                helmet.Hazards = new[] { heat };
                helmet.VentilationZones = System.Array.Empty<VentilationZone>();
                var scenarios = controllerObject.AddComponent<ScenarioController>();
                scenarios.Helmet = helmet;
                scenarios.TemperatureTarget = heatObject.transform.position;

                scenarios.Activate(ScenarioKind.TemperatureHigh);

                Assert.That(helmet.Current.Temperature, Is.EqualTo(66f));
                Assert.That(helmet.Safety.RiskLevel, Is.EqualTo("CRITICAL"));
            }
            finally
            {
                Object.DestroyImmediate(heatObject);
                Object.DestroyImmediate(controllerObject);
                Object.DestroyImmediate(helmetObject);
            }
        }
    }
}
