using SmartRescueHelmet.Unity.Devices;
using SmartRescueHelmet.Unity.Environment;
using SmartRescueHelmet.Unity.Networking;
using SmartRescueHelmet.Unity.Player;
using SmartRescueHelmet.Unity.Presentation;
using SmartRescueHelmet.Unity.Rescue;
using SmartRescueHelmet.Unity.Scenarios;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace SmartRescueHelmet.Unity.Bootstrap
{
    public sealed class RuntimeBootstrap : MonoBehaviour
    {
        private bool _initialized;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void RegisterSceneBootstrap()
        {
            SceneManager.sceneLoaded -= EnsureActiveSceneBootstrap;
            SceneManager.sceneLoaded += EnsureActiveSceneBootstrap;
        }

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void CreateAtRuntime()
        {
            EnsureActiveSceneBootstrap(SceneManager.GetActiveScene(), LoadSceneMode.Single);
        }

        private static void EnsureActiveSceneBootstrap(Scene _, LoadSceneMode __)
        {
            var bootstrap = FindAnyObjectByType<RuntimeBootstrap>();
            if (bootstrap == null)
                bootstrap = new GameObject("RuntimeBootstrap").AddComponent<RuntimeBootstrap>();
            bootstrap.InitializeForActiveScene();
        }

        private void Awake() => InitializeForActiveScene();

        public void InitializeForActiveScene()
        {
            if (_initialized) return;
            _initialized = true;
            Debug.Log("[SRH] RuntimeBootstrap initialized scene=" + SceneManager.GetActiveScene().name);
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
            var rescuer = helmet.AddComponent<RescuerController>();
            var mission = CreateRescueMission(environment);
            hud.Mission = mission;
            hud.Rescuer = rescuer;
            var cameras = CreateCameras(helmet.transform);
            hud.Cameras = cameras;
        }

        private static RescueMission CreateRescueMission(RescueEnvironment environment)
        {
            var mission = new GameObject("RescueMission").AddComponent<RescueMission>();
            var safeZonePosition = environment == RescueEnvironment.BuildingFire
                ? new Vector3(-3.5f, .05f, -5.5f)
                : new Vector3(0f, .05f, -4.25f);
            var safeZone = GameObject.CreatePrimitive(PrimitiveType.Cube);
            safeZone.name = "SafeZone";
            safeZone.transform.position = safeZonePosition;
            safeZone.transform.localScale = new Vector3(3f, .1f, 3f);
            safeZone.GetComponent<Renderer>().material.color = new Color(.08f, .75f, .3f);
            safeZone.AddComponent<SafeZone>();
            CreateSafeZoneBeacons(safeZonePosition);

            var firstPosition = environment == RescueEnvironment.BuildingFire
                ? new Vector3(-2.5f, 1f, 2.5f)
                : new Vector3(-2f, 1f, 1f);
            var secondPosition = environment == RescueEnvironment.BuildingFire
                ? new Vector3(2.5f, 1f, -2.5f)
                : new Vector3(2f, 1f, 3f);
            mission.Register(CreateVictim("Victim Alpha", firstPosition, new Color(.9f, .35f, .2f)));
            mission.Register(CreateVictim("Victim Bravo", secondPosition, new Color(.8f, .2f, .45f)));
            return mission;
        }

        private static RescueVictim CreateVictim(string victimName, Vector3 position, Color uniformColor)
        {
            var victim = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            victim.name = victimName;
            victim.transform.position = position;
            victim.GetComponent<Renderer>().material.color = uniformColor;
            var rigidbody = victim.AddComponent<Rigidbody>();
            rigidbody.isKinematic = true;
            var behavior = victim.AddComponent<RescueVictim>();

            var head = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            head.name = victimName + " Head";
            head.transform.SetParent(victim.transform);
            head.transform.localPosition = new Vector3(0f, 1f, 0f);
            head.transform.localScale = Vector3.one * .38f;
            head.GetComponent<Renderer>().material.color = new Color(.95f, .72f, .52f);
            Destroy(head.GetComponent<Collider>());
            CreateVictimLimb(victim.transform, victimName + " Left Arm", new Vector3(-.42f, .25f, 0f), new Vector3(.14f, .6f, .14f), uniformColor, 15f);
            CreateVictimLimb(victim.transform, victimName + " Right Arm", new Vector3(.42f, .25f, 0f), new Vector3(.14f, .6f, .14f), uniformColor, -15f);
            CreateVictimLimb(victim.transform, victimName + " Left Leg", new Vector3(-.18f, -.8f, 0f), new Vector3(.18f, .7f, .18f), new Color(.12f, .15f, .2f), 0f);
            CreateVictimLimb(victim.transform, victimName + " Right Leg", new Vector3(.18f, -.8f, 0f), new Vector3(.18f, .7f, .18f), new Color(.12f, .15f, .2f), 0f);

            var marker = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            marker.name = victimName + " Rescue Marker";
            marker.transform.SetParent(victim.transform);
            marker.transform.localPosition = new Vector3(0f, 2.25f, 0f);
            marker.transform.localScale = new Vector3(.2f, .45f, .2f);
            Destroy(marker.GetComponent<Collider>());
            var markerLight = marker.AddComponent<Light>();
            markerLight.type = LightType.Point;
            markerLight.range = 3.5f;
            markerLight.intensity = 2f;
            var markerBehavior = marker.AddComponent<RescueVictimMarker>();
            markerBehavior.Victim = behavior;
            markerBehavior.MarkerRenderer = marker.GetComponent<Renderer>();
            markerBehavior.MarkerLight = markerLight;
            return behavior;
        }

        private static void CreateVictimLimb(Transform parent, string limbName, Vector3 localPosition, Vector3 localScale, Color color, float zRotation)
        {
            var limb = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            limb.name = limbName;
            limb.transform.SetParent(parent);
            limb.transform.localPosition = localPosition;
            limb.transform.localScale = localScale;
            limb.transform.localRotation = Quaternion.Euler(0f, 0f, zRotation);
            limb.GetComponent<Renderer>().material.color = color;
            Destroy(limb.GetComponent<Collider>());
        }

        private static void CreateSafeZoneBeacons(Vector3 center)
        {
            var offsets = new[]
            {
                new Vector3(-1.25f, 1.15f, -1.25f), new Vector3(1.25f, 1.15f, -1.25f),
                new Vector3(-1.25f, 1.15f, 1.25f), new Vector3(1.25f, 1.15f, 1.25f),
            };
            foreach (var offset in offsets)
            {
                var beacon = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                beacon.name = "SafeZone Beacon";
                beacon.transform.position = center + offset;
                beacon.transform.localScale = new Vector3(.16f, 1.1f, .16f);
                beacon.GetComponent<Renderer>().material.color = new Color(.05f, 1f, .3f);
                Destroy(beacon.GetComponent<Collider>());
                var light = beacon.AddComponent<Light>();
                light.type = LightType.Point;
                light.color = new Color(.05f, 1f, .3f);
                light.range = 4f;
                light.intensity = 2f;
            }
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
                scenarios.TemperatureTarget = new Vector3(2.65f, 1f, 0f);
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
            CreateFireFlame(new Vector3(4f, 1.55f, 0f), new Vector3(.65f, 1.6f, .65f), new Color(1f, .48f, .03f));
            CreateFireFlame(new Vector3(3.55f, 1.25f, .15f), new Vector3(.45f, 1.1f, .45f), new Color(1f, .82f, .05f));
            CreateFireFlame(new Vector3(4.45f, 1.2f, -.1f), new Vector3(.4f, 1f, .4f), new Color(1f, .35f, .02f));
            CreateSmokePuff(new Vector3(3.8f, 2.6f, 0f), 1.0f);
            CreateSmokePuff(new Vector3(4.35f, 3.2f, .15f), .8f);
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

        private static void CreateFireFlame(Vector3 position, Vector3 scale, Color color)
        {
            var flame = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            flame.name = "FireFlame";
            flame.transform.position = position;
            flame.transform.localScale = scale;
            flame.GetComponent<Renderer>().material.color = color;
            Destroy(flame.GetComponent<Collider>());
        }

        private static void CreateSmokePuff(Vector3 position, float scale)
        {
            var smoke = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            smoke.name = "SmokePuff";
            smoke.transform.position = position;
            smoke.transform.localScale = Vector3.one * scale;
            smoke.GetComponent<Renderer>().material.color = new Color(.18f, .18f, .18f);
            Destroy(smoke.GetComponent<Collider>());
        }

        private static CameraModeController CreateCameras(Transform rescuer)
        {
            var first = new GameObject("FirstPersonCamera").AddComponent<Camera>();
            first.transform.SetParent(rescuer); first.transform.localPosition = new Vector3(0, .6f, 0);
            var command = new GameObject("CommandCenterCamera").AddComponent<Camera>();
            command.transform.position = new Vector3(10, 8, -10); command.transform.LookAt(rescuer);
            var commandFollow = command.gameObject.AddComponent<CommandCenterCameraFollow>();
            commandFollow.Target = rescuer;
            var modes = rescuer.gameObject.AddComponent<CameraModeController>();
            modes.FirstPersonCamera = first; modes.CommandCenterCamera = command;
            return modes;
        }
    }
}
