# Unity 3D Rescue Simulator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Unity-based, physics-consistent rescue training simulator that publishes the existing SMART RESCUE HELMET MQTT contract, applies local fail-safe actuator logic, and provides both first-person and command-center views.

**Architecture:** A standalone `unity-simulator/` Unity 6 LTS URP project owns only virtual-world physics, virtual device inputs, local safety/actuators, and MQTT/WebSocket clients. Its C# DTOs map exactly to the existing M2 contract; FastAPI remains the authority for persistence, backend safety, device state, offline detection, WebSocket envelopes, and the React dashboard.

**Tech Stack:** Unity 6 LTS, URP, C#/.NET Standard 2.1 compatible packages, Unity Test Framework, MQTTnet (desktop MQTT client), `ClientWebSocket` (desktop FastAPI WebSocket client), Newtonsoft.Json, JSON Schema validation package compatible with the selected Unity editor.

**Spec:** `docs/superpowers/specs/2026-09-25-unity-rescue-simulator-design.md`

## Global Constraints

- Preserve existing M1-M10 services, Python simulator, MQTT topics, schemas, Safety Engine thresholds, backend, and React dashboard.
- Use only `helmet/{device_id}/telemetry`, `/status`, `/health`, and `/event` topics, all with schema version `1.0`.
- Use an ISO-8601 timestamp with an offset and `source: "SIMULATOR"` in every outbound message.
- Use FastAPI `/ws` only as a backend-state consumer; Unity must not create a competing business-logic path.
- Local safety must complete before network publish and must operate during MQTT loss.
- Do not implement CFD/FDS, a persistent offline message queue, ESP32 firmware, database migrations, or a new dashboard.
- Keep the workspace’s existing changes intact. Do not run `git add`, `git commit`, `git push`, `git merge`, `git rebase`, `git reset`, or `git checkout`.
- Stop and report if Unity Editor/required compatible packages cannot be installed; do not silently substitute a non-Unity project.

---

## File Structure

```text
unity-simulator/
  Assets/
    Scenes/
      BuildingFire.unity
      ConfinedSpaceCO.unity
      Bootstrap.unity
    Prefabs/
      RescuerHelmet.prefab
      HazardVolume.prefab
      VentilationZone.prefab
    Scripts/
      Contracts/
        HelmetMessages.cs
        HelmetTopicBuilder.cs
        JsonContractValidator.cs
      Configuration/
        SimulatorSettings.cs
      Devices/
        DeviceSensorSnapshot.cs
        TemperatureSensorAdapter.cs
        CoSensorAdapter.cs
        ImuSensorAdapter.cs
        BatterySimulator.cs
        LocalSafetyEvaluator.cs
        VirtualActuatorController.cs
        HelmetDeviceController.cs
      Environment/
        HazardVolume.cs
        VentilationZone.cs
        FallZone.cs
      Networking/
        MqttDevicePublisher.cs
        BackendWebSocketClient.cs
      Player/
        RescuerController.cs
        CameraModeController.cs
      Scenarios/
        ScenarioDefinition.cs
        ScenarioController.cs
      Presentation/
        VisorHudController.cs
        CommandCenterOverlay.cs
      Tests/EditMode/
        ContractTests.cs
        SensorAndSafetyTests.cs
        ActuatorTests.cs
        PublisherTests.cs
      Tests/PlayMode/
        SceneAndCameraTests.cs
        HazardFailSafeTests.cs
    StreamingAssets/
      contracts/
        telemetry.schema.json
        status.schema.json
        health.schema.json
        event.schema.json
  Packages/
  ProjectSettings/
  README.md
```

## Task 1: Unity project foundation and contract assets

**Files:**
- Create: `unity-simulator/` Unity 6 LTS URP project files.
- Create: `unity-simulator/Assets/Scripts/Configuration/SimulatorSettings.cs`.
- Create: `unity-simulator/Assets/Scripts/Contracts/HelmetMessages.cs`.
- Create: `unity-simulator/Assets/Scripts/Contracts/HelmetTopicBuilder.cs`.
- Create: `unity-simulator/Assets/Scripts/Contracts/JsonContractValidator.cs`.
- Create: `unity-simulator/Assets/StreamingAssets/contracts/*.schema.json` copied verbatim from `shared/contracts/`.
- Create: `unity-simulator/Assets/Tests/EditMode/ContractTests.cs`.
- Create: `unity-simulator/Assets/Tests/TestSupport.cs`.
- Create: `unity-simulator/README.md`.

**Interfaces:**
- Consumes: the JSON schemas in `shared/contracts/` and topic patterns in `shared/mqtt_topics.md`.
- Produces: `TelemetryMessage`, `DeviceStatusMessage`, `DeviceHealthMessage`, `EventMessage`, `HelmetTopicBuilder`, `JsonContractValidator`, and `SimulatorSettings` for every later task.

- [ ] **Step 1: Verify Unity tooling before creating files**

Run `Unity.exe -version` (or inspect Unity Hub’s installed editor list). Record the exact Unity 6 LTS version in `unity-simulator/README.md`. In Package Manager, install a desktop-compatible MQTTnet version, Newtonsoft.Json, and a JSON-Schema validator compatible with that editor’s scripting runtime; record exact package IDs and versions in `Packages/manifest.json` and README.

- [ ] **Step 2: Write failing contract tests**

```csharp
[Test]
public void Telemetry_dto_serializes_a_valid_milestone_2_payload()
{
    var payload = TestMessages.Telemetry("FF01");
    Assert.That(_validator.IsValid("telemetry.schema.json", payload), Is.True);
}

[TestCase("FF01", "helmet/FF01/telemetry")]
[TestCase("FF02", "helmet/FF02/health")]
public void Topic_builder_uses_the_contract(string deviceId, string expected)
{
    var suffix = expected.Split('/')[2];
    Assert.That(HelmetTopicBuilder.Build(deviceId, suffix), Is.EqualTo(expected));
}
```

- [ ] **Step 3: Run edit-mode tests and confirm red state**

Run from Unity Test Runner: `ContractTests`. Expected: compilation/test failure because DTOs, topic builder, and validator do not exist.

- [ ] **Step 4: Implement contract DTOs and validator**

```csharp
public sealed record MessageBase(
    [property: JsonProperty("schema_version")] string SchemaVersion,
    [property: JsonProperty("device_id")] string DeviceId,
    [property: JsonProperty("timestamp")] DateTimeOffset Timestamp,
    [property: JsonProperty("source")] string Source);

public static class HelmetTopicBuilder
{
    public static string Build(string deviceId, string suffix) =>
        $"helmet/{ValidateDeviceId(deviceId)}/{ValidateSuffix(suffix)}";
}
```

Use `JsonContractValidator.ValidateOrThrow(schemaFileName, json)` before any publish. The validator loads only the copied M2 JSON schemas from `StreamingAssets/contracts`; it never maintains a second manual schema.

Define `TelemetryMessage.CreateNormal(string deviceId, DateTimeOffset timestamp)` as a static factory that fills every required M2 field with a valid normal WALKING payload; define equivalent explicit constructors/factories for `DeviceStatusMessage` and `DeviceHealthMessage`. Every DTO property must carry its JSON field name and use string enum values matching `shared/enums.md`.

Create the explicit test helpers used in the tests:

```csharp
public static class TestMessages
{
    public static TelemetryMessage Telemetry(string deviceId) =>
        TelemetryMessage.CreateNormal(deviceId, new DateTimeOffset(2026, 9, 25, 9, 0, 0, TimeSpan.FromHours(7)));
}

public static class TestSnapshots
{
    public static DeviceSensorSnapshot WithTemperature(float temperature) =>
        DeviceSensorSnapshot.Normal("FF01") with { Temperature = temperature };
}
```

- [ ] **Step 5: Run contract tests and inspect output**

Run `ContractTests` in Unity Test Runner. Expected: all pass, including a test that rejects a missing `device_id`, a timezone-free timestamp, invalid risk/event enum, invalid battery, and an incomplete IMU object. Run `git diff --check`; do not commit.

## Task 2: Deterministic sensors, local safety, and virtual actuators

**Files:**
- Create: `unity-simulator/Assets/Scripts/Devices/DeviceSensorSnapshot.cs`.
- Create: `unity-simulator/Assets/Scripts/Devices/TemperatureSensorAdapter.cs`.
- Create: `unity-simulator/Assets/Scripts/Devices/CoSensorAdapter.cs`.
- Create: `unity-simulator/Assets/Scripts/Devices/ImuSensorAdapter.cs`.
- Create: `unity-simulator/Assets/Scripts/Devices/BatterySimulator.cs`.
- Create: `unity-simulator/Assets/Scripts/Devices/LocalSafetyEvaluator.cs`.
- Create: `unity-simulator/Assets/Scripts/Devices/VirtualActuatorController.cs`.
- Create: `unity-simulator/Assets/Tests/EditMode/SensorAndSafetyTests.cs`.
- Create: `unity-simulator/Assets/Tests/EditMode/ActuatorTests.cs`.

**Interfaces:**
- Consumes: `HazardSample`, `RescuerMotion`, `SimulatorSettings`.
- Produces: `DeviceSensorSnapshot Read(...)`, `LocalSafetyResult Evaluate(DeviceSensorSnapshot)`, and `ActuatorState Apply(LocalSafetyResult)`.

- [ ] **Step 1: Write failing safety and actuator tests**

```csharp
[Test]
public void Critical_temperature_maps_to_red_buzzer_and_vibration()
{
    var result = _safety.Evaluate(TestSnapshots.WithTemperature(60f));
    var state = _actuators.Apply(result);
    Assert.Multiple(() => {
        Assert.That(result.RiskLevel, Is.EqualTo("CRITICAL"));
        Assert.That(state.Led, Is.EqualTo("RED"));
        Assert.That(state.Buzzer, Is.True);
        Assert.That(state.Vibration, Is.True);
    });
}
```

- [ ] **Step 2: Run tests to confirm red state**

Run `SensorAndSafetyTests` and `ActuatorTests` in Unity Test Runner. Expected: failure because device/safety/actuator types do not exist.

- [ ] **Step 3: Implement deterministic device components**

Implement `DeviceSensorSnapshot` containing nullable temperature/CO, six IMU values, battery, Wi-Fi/MQTT connection status, movement, fall, immobile, and SOS. Apply exactly the current backend thresholds: temperature warning/critical `50/60`, CO `50/100`, battery `<= 20`, SOS/fall critical, and no new independent immobility rule. Seed small sensor variance through `System.Random(seed)` from `SimulatorSettings`.

```csharp
public sealed record HazardSample(float TemperatureDelta, float CoPpm, float Visibility);
public sealed record LocalSafetyResult(string RiskLevel, bool Fall, bool Immobile, bool Sos);
public sealed record ActuatorState(string Led, bool Buzzer, bool Vibration);
public sealed record DeviceSensorSnapshot(
    float? Temperature, float? Co, ImuReading Imu, float Battery,
    string Wifi, string Mqtt, string Movement, bool Fall, bool Immobile, bool Sos)
{
    public static DeviceSensorSnapshot Normal(string deviceId) =>
        new(31f, 5f, ImuReading.Walking(), 85f, "CONNECTED", "CONNECTED", "WALKING", false, false, false);
}
```

```csharp
public ActuatorState Apply(LocalSafetyResult safety) => safety.RiskLevel switch
{
    "CRITICAL" => new("RED", true, true),
    "WARNING" => new("YELLOW", false, false),
    _ => new("GREEN", false, false)
};
```

- [ ] **Step 4: Run edit-mode safety regression**

Run `SensorAndSafetyTests` and `ActuatorTests`. Expected: deterministic normal values remain valid; warning uses yellow; temperature/CO/fall/SOS/low-battery critical use RED/ON/ON. Run `git diff --check`; do not commit.

## Task 3: Environment hazards and rescuer physics

**Files:**
- Create: `unity-simulator/Assets/Scripts/Environment/HazardVolume.cs`.
- Create: `unity-simulator/Assets/Scripts/Environment/VentilationZone.cs`.
- Create: `unity-simulator/Assets/Scripts/Environment/FallZone.cs`.
- Create: `unity-simulator/Assets/Scripts/Player/RescuerController.cs`.
- Create: `unity-simulator/Assets/Prefabs/HazardVolume.prefab`.
- Create: `unity-simulator/Assets/Prefabs/VentilationZone.prefab`.
- Create: `unity-simulator/Assets/Tests/PlayMode/HazardFailSafeTests.cs`.

**Interfaces:**
- Consumes: player transform/velocity and `HazardVolume.Sample(Vector3 position, float time)`.
- Produces: aggregate `HazardSample` plus local fall/SOS inputs for `HelmetDeviceController`.

- [ ] **Step 1: Write failing play-mode hazard test**

```csharp
[UnityTest]
public IEnumerator Entering_critical_heat_volume_updates_local_actuators_without_mqtt()
{
    _publisher.PublishEnabled = false;
    _player.transform.position = _criticalHeat.transform.position;
    yield return null;
    Assert.That(_helmet.CurrentActuatorState.Led, Is.EqualTo("RED"));
    Assert.That(_publisher.PublishCallCount, Is.Zero);
}
```

- [ ] **Step 2: Run the isolated play-mode test and confirm red state**

Run `HazardFailSafeTests`. Expected: failure because hazard/player/helmet components are missing.

- [ ] **Step 3: Implement reusable physical environment components**

Use trigger colliders for `HazardVolume` and `VentilationZone`. A volume sample must be a deterministic function of local distance, profile curve, and scene time. `VentilationZone` reduces only CO contribution. `RescuerController` uses Unity collision/ground detection and exposes velocity-derived IMU movement; `FallZone` calls `ReportFall()` once per controlled fall. Do not represent rendered smoke/fire particles as sensor truth.

- [ ] **Step 4: Run play-mode checks**

Run `HazardFailSafeTests`. Expected: entering/leaving hazard changes sensor snapshot; fall produces critical local state; disabling MQTT does not stop actuator transition. Run `git diff --check`; do not commit.

## Task 4: Helmet prefab, publish pipeline, and MQTT resilience

**Files:**
- Create: `unity-simulator/Assets/Scripts/Devices/HelmetDeviceController.cs`.
- Create: `unity-simulator/Assets/Scripts/Networking/MqttDevicePublisher.cs`.
- Create: `unity-simulator/Assets/Prefabs/RescuerHelmet.prefab`.
- Create: `unity-simulator/Assets/Tests/EditMode/PublisherTests.cs`.
- Modify: `unity-simulator/Assets/Scripts/Contracts/HelmetMessages.cs`.

**Interfaces:**
- Consumes: `DeviceSensorSnapshot`, `LocalSafetyResult`, `ActuatorState`, `SimulatorSettings`, `HelmetTopicBuilder`, `JsonContractValidator`.
- Produces: `Tick(float deltaTime)`, `SetPublishingEnabled(bool)`, `ConnectAsync()`, `DisconnectAsync()`, and `PublishIfDueAsync()`.

- [ ] **Step 1: Write failing publisher tests**

```csharp
[Test]
public async Task Disabled_transport_evaluates_actuators_but_does_not_publish()
{
    _transport.SetConnected(false);
    await _helmet.PublishIfDueAsync();
    Assert.That(_transport.PublishedMessages, Is.Empty);
    Assert.That(_helmet.CurrentActuatorState.Led, Is.EqualTo("GREEN"));
}

[Test]
public async Task Reconnect_resumes_validated_telemetry_publish()
{
    _transport.SetConnected(true);
    await _helmet.PublishIfDueAsync();
    Assert.That(_transport.PublishedMessages.Single().Topic,
        Is.EqualTo("helmet/FF01/telemetry"));
}
```

- [ ] **Step 2: Run publisher tests to confirm red state**

Run `PublisherTests`. Expected: compilation failure because the controller/publisher methods do not exist.

- [ ] **Step 3: Implement publish ordering and resilient transport**

`HelmetDeviceController` must always execute `Read sensors -> Evaluate local safety -> Apply actuators -> construct DTO -> JSON schema validation -> MQTT publish`. Use MQTT QoS 1 for status/health and QoS 0 for periodic telemetry, matching the existing prototype’s delivery intent. `MqttDevicePublisher` reports state but never allows a failed publish to interrupt local device evaluation. Apply bounded reconnect delay and log transitions only; avoid per-telemetry INFO logs.

Define the testable publisher boundary rather than coupling tests to a live broker:

```csharp
public interface IDeviceTransport
{
    bool IsConnected { get; }
    Task<bool> PublishAsync(string topic, string utf8Json, int qos, CancellationToken cancellationToken);
}

public sealed class MqttDevicePublisher : IDeviceTransport
{
    public bool PublishEnabled { get; private set; }
    public void SetPublishingEnabled(bool enabled) => PublishEnabled = enabled;
    public Task ConnectAsync(CancellationToken cancellationToken);
    public Task DisconnectAsync();
    public Task<bool> PublishAsync(string topic, string utf8Json, int qos, CancellationToken cancellationToken);
}
```

Use an in-memory `RecordingTransport` in `PublisherTests` with `PublishedMessages` and `PublishCallCount`; do not put test-only counters on `MqttDevicePublisher`.

- [ ] **Step 4: Build the helmet prefab**

Create a procedural/detail-ready prefab hierarchy: shell, visor, IMU mount, temperature/CO sensor mounts, LED emissive element, buzzer indicator, vibration indicator, and HUD anchor. Bind material/light state only through `VirtualActuatorController`; no UI component directly decides actuator colours.

- [ ] **Step 5: Run MQTT/unit regression**

Run `ContractTests`, `SensorAndSafetyTests`, `ActuatorTests`, and `PublisherTests`. Expected: payloads validate before transport; disabled MQTT has zero messages; reconnect can publish again; invalid payload blocks publication. Run `git diff --check`; do not commit.

## Task 5: Both cameras and accessible Unity overlays

**Files:**
- Create: `unity-simulator/Assets/Scripts/Player/CameraModeController.cs`.
- Create: `unity-simulator/Assets/Scripts/Presentation/VisorHudController.cs`.
- Create: `unity-simulator/Assets/Scripts/Presentation/CommandCenterOverlay.cs`.
- Create: `unity-simulator/Assets/Scripts/Networking/BackendWebSocketClient.cs`.
- Create: `unity-simulator/Assets/Tests/PlayMode/SceneAndCameraTests.cs`.

**Interfaces:**
- Consumes: `HelmetDeviceController.CurrentSnapshot`, `CurrentSafety`, `CurrentActuatorState`, and backend `/ws` envelopes.
- Produces: `SetMode(CameraMode)`, `RenderDeviceState(DeviceStateEnvelope)`, and a bounded WebSocket reconnect loop.

- [ ] **Step 1: Write failing camera and display tests**

```csharp
[UnityTest]
public IEnumerator Switching_to_command_center_disables_first_person_camera()
{
    _cameras.SetMode(CameraMode.CommandCenter);
    yield return null;
    Assert.That(_firstPerson.enabled, Is.False);
    Assert.That(_commandCenter.enabled, Is.True);
}
```

- [ ] **Step 2: Run scene/camera tests to confirm red state**

Run `SceneAndCameraTests`. Expected: failure because camera and overlay components do not exist.

- [ ] **Step 3: Implement views and backend state client**

First-person display shows textual risk level, device ID, temperature, CO, battery, Wi-Fi, MQTT, and actuator state. Command-center is an external camera plus a readable state overlay driven only by `/ws` messages. Use a background receive loop and marshal Unity object updates back to the main thread. On parse/connection errors show `DISCONNECTED`; do not crash the scene and do not synthesize offline business state.

- [ ] **Step 4: Run play-mode accessibility and resilience checks**

Run `SceneAndCameraTests`. Expected: either view changes on input, overlays contain text labels for risk/severity, a closed WebSocket triggers retry without killing simulation. Run `git diff --check`; do not commit.

## Task 6: Scenarios and BuildingFire scene

**Files:**
- Create: `unity-simulator/Assets/Scripts/Scenarios/ScenarioDefinition.cs`.
- Create: `unity-simulator/Assets/Scripts/Scenarios/ScenarioController.cs`.
- Create: `unity-simulator/Assets/Scenes/BuildingFire.unity`.
- Create: `unity-simulator/Assets/Tests/PlayMode/BuildingFireScenarioTests.cs`.

**Interfaces:**
- Consumes: `HelmetDeviceController`, `HazardVolume`, `FallZone`, `MqttDevicePublisher`.
- Produces: `Activate(ScenarioKind kind)`, `ResetScenario()`, deterministic scene placement/control state.

- [ ] **Step 1: Write failing BuildingFire scenario test**

```csharp
[UnityTest]
public IEnumerator Temperature_high_scenario_reaches_critical_local_state()
{
    _scenarios.Activate(ScenarioKind.TemperatureHigh);
    yield return new WaitForSeconds(0.1f);
    Assert.That(_helmet.CurrentSafety.RiskLevel, Is.EqualTo("CRITICAL"));
}
```

- [ ] **Step 2: Run the scenario test and confirm red state**

Run `BuildingFireScenarioTests`. Expected: failure because the scene/controller/enum does not exist.

- [ ] **Step 3: Construct BuildingFire from reusable components**

Use static colliders for rooms/debris, `HazardVolume` instances for heat, particle/fog visuals for smoke, a `FallZone`, and spawn/reset points. Implement NORMAL, TEMPERATURE_HIGH, FALL, SOS, LOW_BATTERY, CONNECTION_LOSS, and RECONNECT selection through `ScenarioController`; connection loss toggles publisher transport only, never local safety.

- [ ] **Step 4: Run BuildingFire play-mode tests**

Run `BuildingFireScenarioTests` and `HazardFailSafeTests`. Expected: each configured scenario produces the documented local result, and CONNECTION_LOSS still produces local critical actuator state. Run `git diff --check`; do not commit.

## Task 7: ConfinedSpaceCO scene

**Files:**
- Create: `unity-simulator/Assets/Scenes/ConfinedSpaceCO.unity`.
- Create: `unity-simulator/Assets/Tests/PlayMode/ConfinedSpaceScenarioTests.cs`.
- Modify: `unity-simulator/Assets/Scripts/Scenarios/ScenarioController.cs`.

**Interfaces:**
- Consumes: shared rescuer/helmet prefab, CO `HazardVolume`, `VentilationZone`, shared scenario controller.
- Produces: a independently loadable scene that exercises NORMAL and CO_HIGH with matching device messages.

- [ ] **Step 1: Write failing confined-space test**

```csharp
[UnityTest]
public IEnumerator Co_high_inside_hazard_is_critical_and_ventilation_reduces_value()
{
    _scenarios.Activate(ScenarioKind.CoHigh);
    yield return null;
    Assert.That(_helmet.CurrentSnapshot.Co, Is.GreaterThanOrEqualTo(100f));
    Assert.That(_helmet.CurrentSafety.RiskLevel, Is.EqualTo("CRITICAL"));
}
```

- [ ] **Step 2: Run test to confirm red state**

Run `ConfinedSpaceScenarioTests`. Expected: scene and configured CO hazard do not yet exist.

- [ ] **Step 3: Construct ConfinedSpaceCO and connect the scenario**

Create narrow collision corridors, a low-visibility treatment, CO hazard volumes, and one or more ventilation zones. Use the same prefab/controller code as BuildingFire; only scene assets and volume profiles differ. Confirm scenario reset restores normal CO and actuator state.

- [ ] **Step 4: Run the confined-space suite**

Run `ConfinedSpaceScenarioTests` with prior edit-mode suites. Expected: CO HIGH becomes CRITICAL, a ventilation zone lowers aggregate CO deterministically, and normal reset is GREEN/OFF/OFF. Run `git diff --check`; do not commit.

## Task 8: Full local integration runbook and regression verification

**Files:**
- Modify: `unity-simulator/README.md`.
- Modify: root `README.md` only if it has no user-owned change conflict; otherwise leave it unchanged and document Unity solely in `unity-simulator/README.md`.
- Create: `unity-simulator/docs/integration-runbook.md`.

**Interfaces:**
- Consumes: complete Unity project, existing Docker services, `/ws`, Mosquitto, and FastAPI APIs.
- Produces: repeatable manual verification evidence and operational launch instructions.

- [ ] **Step 1: Define integration assertions before the run**

Write the following assertions into `integration-runbook.md`: Unity publishes `telemetry`, `status`, and `health` for a configured device ID; FastAPI persists them; React dashboard receives a device state update; TEMPERATURE_HIGH produces backend `TEMPERATURE_HIGH` critical event; MQTT loss yields local RED/ON/ON; reconnect resumes valid publishing.

- [ ] **Step 2: Run Unity edit-mode and play-mode suites**

Run all Unity tests in Test Runner. Expected: zero failed tests; record exact passed/failed/skipped count in the runbook.

- [ ] **Step 3: Run existing stack regression commands**

Run `pytest` from `backend`, `pytest` from `simulator`, `npm run build` from `frontend`, then `docker compose config --quiet` from repository root. Expected: all complete successfully; do not change baseline tests merely to satisfy Unity work.

- [ ] **Step 4: Run a real Unity-to-stack integration**

Start the existing stack with `docker compose up --build -d`; launch one Unity scene configured for a non-conflicting device ID such as `FF03`. Observe Mosquitto topics, call `GET http://localhost:8000/health`, inspect the corresponding API records/device state, and confirm a WebSocket/dashboard update. Repeat with TemperatureHigh and a temporary transport-disable/reconnect action.

- [ ] **Step 5: Record results and check workspace quality**

Append actual commands, observed payload samples, event IDs, database/API evidence, test counts, and known limitations to the runbook. Run `git diff --check` and `git status --short`; do not add, commit, or discard any files.

## Plan Self-Review

- Spec coverage: Tasks 1–2 cover contract, deterministic virtual sensors, local safety, and actuators; Tasks 3–4 cover physics, helmet, MQTT and fail-safe transport; Task 5 covers both views and backend WebSocket consumption; Tasks 6–7 cover the two environments/scenarios; Task 8 covers regression and live end-to-end evidence.
- Scope: The plan explicitly excludes CFD/FDS, persistent offline queues, database/API contract changes, and React dashboard replacement.
- Consistency: every scenario and network participant uses `HelmetDeviceController` and the existing topic/DTO contract; all local safety paths reach `VirtualActuatorController` before transport.
- Placeholder scan: no deferred implementation placeholders; package compatibility is an explicit prerequisite with a stop condition, not an alternative implementation.
