using SmartRescueHelmet.Unity.Devices;
using SmartRescueHelmet.Unity.Environment;
using SmartRescueHelmet.Unity.Networking;
using SmartRescueHelmet.Unity.Player;
using SmartRescueHelmet.Unity.Presentation;
using SmartRescueHelmet.Unity.Scenarios;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace SmartRescueHelmet.Unity.Bootstrap
{
    public sealed class RuntimeBootstrap : MonoBehaviour
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void CreateAtRuntime()
        {
            if (FindAnyObjectByType<RuntimeBootstrap>() == null)
                new GameObject("RuntimeBootstrap").AddComponent<RuntimeBootstrap>();
        }
        private void Awake()
        {
            Debug.Log("[SRH] RuntimeBootstrap Awake");
            gameObject.AddComponent<RescueSceneNavigator>();
            var environment = EnvironmentSceneSelector.FromSceneName(SceneManager.GetActiveScene().name);
            if (environment == RescueEnvironment.BuildingFire)
                CreateBuildingFireEnvironment();
            else
                CreateConfinedSpaceEnvironment();
            var helmet = new GameObject("RescuerHelmet");
            helmet.transform.position = new Vector3(0, 1, 0);
            var shell = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            shell.name = "HelmetShell"; shell.transform.SetParent(helmet.transform); shell.transform.localPosition = new Vector3(0, .45f, 0); shell.transform.localScale = new Vector3(.8f, .42f, .8f);
            shell.GetComponent<Renderer>().material.color = new Color(.95f, .85f, .12f);
            var visor = GameObject.CreatePrimitive(PrimitiveType.Cube);
            visor.name = "HelmetVisor"; visor.transform.SetParent(helmet.transform); visor.transform.localPosition = new Vector3(0, .35f, .42f); visor.transform.localScale = new Vector3(.62f, .18f, .04f);
            visor.GetComponent<Renderer>().material.color = new Color(.08f, .25f, .32f);
            var actuator = helmet.AddComponent<VirtualActuatorController>();
            var led = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            led.name = "HelmetSafetyLED"; led.transform.SetParent(helmet.transform); led.transform.localPosition = new Vector3(0, .35f, .25f); led.transform.localScale = Vector3.one * .12f;
            actuator.LedRenderer = led.GetComponent<Renderer>();
            var buzzer = GameObject.CreatePrimitive(PrimitiveType.Cube);
            buzzer.name = "HelmetBuzzerIndicator"; buzzer.transform.SetParent(helmet.transform); buzzer.transform.localPosition = new Vector3(-.18f, .36f, .25f); buzzer.transform.localScale = Vector3.one * .1f;
            actuator.BuzzerIndicator = buzzer.GetComponent<Renderer>();
            var vibration = GameObject.CreatePrimitive(PrimitiveType.Cube);
            vibration.name = "HelmetVibrationIndicator"; vibration.transform.SetParent(helmet.transform); vibration.transform.localPosition = new Vector3(.18f, .36f, .25f); vibration.transform.localScale = Vector3.one * .1f;
            actuator.VibrationIndicator = vibration.GetComponent<Renderer>();
            var publisher = helmet.AddComponent<MqttDevicePublisher>();
            var backendRealtime = helmet.AddComponent<BackendWebSocketClient>();
            var device = helmet.AddComponent<HelmetDeviceController>();
            device.Actuators = actuator; device.Publisher = publisher;
            var scenarios = helmet.AddComponent<ScenarioController>(); scenarios.Helmet = device; scenarios.NormalSpawn = helmet.transform.position;
            var hud = helmet.AddComponent<VisorHudController>(); hud.Device = device; hud.Scenarios = scenarios; hud.Publisher = publisher; hud.BackendRealtime = backendRealtime;
            ConfigureEnvironmentHazards(environment, device, scenarios);
            var fallZone = GameObject.CreatePrimitive(PrimitiveType.Cube);
            fallZone.name = "FallZone"; fallZone.transform.position = new Vector3(0, .05f, 5); fallZone.transform.localScale = new Vector3(2, .1f, 2);
            fallZone.GetComponent<Renderer>().material.color = Color.red; fallZone.GetComponent<Collider>().isTrigger = true;
            fallZone.AddComponent<FallZone>().Device = device;
            scenarios.FallTarget = fallZone.transform.position + Vector3.up;
            helmet.AddComponent<CharacterController>();
            helmet.AddComponent<RescuerController>();
            var cameras = CreateCameras(helmet.transform);
            hud.Cameras = cameras;
        }

        private static void ConfigureEnvironmentHazards(
            RescueEnvironment environment,
            HelmetDeviceController device,
            ScenarioController scenarios)
        {
            if (environment == RescueEnvironment.BuildingFire)
            {
                var heat = GameObject.CreatePrimitive(PrimitiveType.Cube);
                heat.name = "TemperatureHazard";
                heat.transform.position = new Vector3(4, 0, 0);
                heat.transform.localScale = new Vector3(3, 3, 3);
                var heatVolume = heat.AddComponent<HazardVolume>();
                heatVolume.TemperatureDelta = 35f;
                scenarios.TemperatureTarget = heat.transform.position;
                scenarios.CoTarget = scenarios.NormalSpawn;
                device.Hazards = new[] { heatVolume };
                device.VentilationZones = System.Array.Empty<VentilationZone>();
                return;
            }

            var coZone = GameObject.CreatePrimitive(PrimitiveType.Cube);
            coZone.name = "ConfinedSpaceCOZone";
            coZone.transform.position = new Vector3(0, 1, 3);
            coZone.transform.localScale = new Vector3(3, 2, 3);
            coZone.GetComponent<Renderer>().material.color = new Color(.55f, .7f, .05f, .35f);
            var coVolume = coZone.AddComponent<HazardVolume>();
            coVolume.CoPpm = 110f;
            scenarios.CoTarget = coZone.transform.position;
            scenarios.TemperatureTarget = scenarios.NormalSpawn;

            var ventilation = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            ventilation.name = "VentilationZone";
            ventilation.transform.position = new Vector3(0, 1, -3);
            ventilation.transform.localScale = new Vector3(1.2f, 1, 1.2f);
            ventilation.GetComponent<Renderer>().material.color = new Color(.1f, .7f, 1f);
            var ventilationZone = ventilation.AddComponent<VentilationZone>();
            ventilationZone.CoReduction = .8f;
            device.Hazards = new[] { coVolume };
            device.VentilationZones = new[] { ventilationZone };
        }

        private static void CreateBuildingFireEnvironment()
        {
            var floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
            floor.name = "BuildingFireFloor";
            floor.transform.localScale = new Vector3(3, 1, 3);
            var fire = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            fire.name = "FireVisual"; fire.transform.position = new Vector3(4, 0.8f, 0);
            fire.transform.localScale = Vector3.one * 1.5f;
            fire.GetComponent<Renderer>().material.color = new Color(1f, .2f, 0f);
            var fireLight = fire.AddComponent<Light>(); fireLight.type = LightType.Point; fireLight.color = new Color(1f, .18f, 0f); fireLight.range = 8f; fireLight.intensity = 5f;
            var particles = fire.AddComponent<ParticleSystem>();
            var main = particles.main; main.startColor = new Color(1f, .18f, 0f); main.startSize = .7f; main.startLifetime = 1.2f; main.startSpeed = 2f;
            var emission = particles.emission; emission.rateOverTime = 35;
            var shape = particles.shape; shape.shapeType = ParticleSystemShapeType.Cone; shape.radius = .5f;
            var smoke = new GameObject("SmokeVisual"); smoke.transform.position = new Vector3(4, 2f, 0);
            var smokeParticles = smoke.AddComponent<ParticleSystem>();
            var smokeMain = smokeParticles.main; smokeMain.startColor = new Color(.2f, .2f, .2f, .45f); smokeMain.startSize = 1.4f; smokeMain.startLifetime = 3f; smokeMain.startSpeed = .6f;
            var smokeEmission = smokeParticles.emission; smokeEmission.rateOverTime = 18;
            CreateWall(new Vector3(0, 1.5f, 8), new Vector3(12, 3, .3f));
            CreateWall(new Vector3(0, 1.5f, -8), new Vector3(12, 3, .3f));
            CreateWall(new Vector3(-6, 1.5f, 0), new Vector3(.3f, 3, 16));
            CreateWall(new Vector3(6, 1.5f, 0), new Vector3(.3f, 3, 16));
            CreateObstacle(new Vector3(1.5f, .5f, 2));
            CreateObstacle(new Vector3(-2f, .5f, -3));
            RenderSettings.fog = true; RenderSettings.fogColor = new Color(.18f, .18f, .18f); RenderSettings.fogDensity = .025f;
            new GameObject("Directional Light").AddComponent<Light>().type = LightType.Directional;
        }

        private static void CreateConfinedSpaceEnvironment()
        {
            var floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
            floor.name = "ConfinedSpaceFloor";
            floor.transform.localScale = new Vector3(2f, 1f, 2f);
            CreateWall(new Vector3(0, 1.5f, 6), new Vector3(8, 3, .3f));
            CreateWall(new Vector3(0, 1.5f, -6), new Vector3(8, 3, .3f));
            CreateWall(new Vector3(-4, 1.5f, 0), new Vector3(.3f, 3, 12));
            CreateWall(new Vector3(4, 1.5f, 0), new Vector3(.3f, 3, 12));
            CreateObstacle(new Vector3(-1.2f, .5f, 0));
            CreateObstacle(new Vector3(1.2f, .5f, 1.5f));
            var warningLight = new GameObject("ConfinedSpaceWarningLight").AddComponent<Light>();
            warningLight.type = LightType.Point;
            warningLight.color = new Color(.65f, .8f, .1f);
            warningLight.range = 7f;
            warningLight.intensity = 3f;
            warningLight.transform.position = new Vector3(0, 2f, 3f);
            RenderSettings.fog = true;
            RenderSettings.fogColor = new Color(.18f, .24f, .12f);
            RenderSettings.fogDensity = .055f;
            new GameObject("Directional Light").AddComponent<Light>().type = LightType.Directional;
        }

        private static void CreateWall(Vector3 position, Vector3 scale)
        {
            var wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
            wall.name = "BuildingWall"; wall.transform.position = position; wall.transform.localScale = scale;
            wall.GetComponent<Renderer>().material.color = new Color(.2f, .22f, .24f);
        }
        private static void CreateObstacle(Vector3 position)
        {
            var obstacle = GameObject.CreatePrimitive(PrimitiveType.Cube);
            obstacle.name = "RescueObstacle"; obstacle.transform.position = position; obstacle.transform.localScale = new Vector3(1.2f, 1, 1.2f);
            obstacle.GetComponent<Renderer>().material.color = new Color(.35f, .2f, .12f);
        }

        private static CameraModeController CreateCameras(Transform rescuer)
        {
            var first = new GameObject("FirstPersonCamera").AddComponent<Camera>();
            first.transform.SetParent(rescuer); first.transform.localPosition = new Vector3(0, .6f, 0);
            var command = new GameObject("CommandCenterCamera").AddComponent<Camera>();
            command.transform.position = new Vector3(10, 8, -10); command.transform.LookAt(rescuer);
            var modes = rescuer.gameObject.AddComponent<CameraModeController>();
            modes.FirstPersonCamera = first; modes.CommandCenterCamera = command;
            return modes;
        }
    }
}
