# Unity 3D Rescue Simulator Design

## Purpose

Add an independent Unity-based simulator to SMART RESCUE HELMET V1. It is a
training-oriented digital twin: a virtual rescuer, helmet, sensors, hazards,
and actuators interact in two rescue environments. It validates the existing
IoT system with the same MQTT contract as the Python simulator and future
ESP32-S3 publisher.

This is not a certified fire, smoke, gas-dispersion, or human-safety model.
Its physics and hazards must be credible and repeatable for software testing,
not used for real-world operational decisions.

## Scope

The Unity simulator provides both selectable viewpoints:

- First-person, through the rescuer's helmet/visor, with a compact safety HUD.
- Command-center, an external camera following the rescuer and displaying the
  backend-processed device state.

It provides two playable scenes:

1. **BuildingFire** — a building interior with static obstacles, collision,
   heat volumes, smoke visual effects, and fire visual effects.
2. **ConfinedSpaceCO** — an enclosed, low-visibility space with CO hazard
   volumes, narrow passages, and ventilation zones.

Both scenes share the same player, helmet, sensor, MQTT, local safety, and
actuator systems.

Out of scope: CFD/FDS integration, certified physical modelling, real ESP32
firmware, changes to backend safety thresholds, new MQTT topics, database
schema changes, and a replacement for the existing React dashboard.

## System Boundary
ok
Unity is a separate project at `unity-simulator/`. It can run alongside the
Python simulator for comparison or replace it by selecting one publisher in
the Docker/local runtime configuration. It does not import Python backend code
or modify its ownership of persistence, global safety decisions, WebSocket,
or the React dashboard.

```text
Unity physics scenes
  -> virtual sensors -> Unity local safety -> virtual actuators
  -> MQTT publisher (existing message contract)
  -> Mosquitto -> FastAPI subscriber -> validation/safety/state/persistence
  -> WebSocket -> React Dashboard

FastAPI WebSocket
  -> Unity command-center display (read-only backend state)
```

## MQTT and Data Contract

Unity publishes only the already-defined topics:

- `helmet/{device_id}/telemetry`
- `helmet/{device_id}/status`
- `helmet/{device_id}/health`
- `helmet/{device_id}/event` only where a device-originated scenario genuinely
  needs an event message.

Messages retain `schema_version: "1.0"`, a multi-device `device_id`, an
ISO-8601 timezone-aware timestamp, `source: "SIMULATOR"`, and all existing
Pydantic/JSON-schema field names and enum values. Unity validates its outgoing
DTOs against an exported representation of the shared schema before publish.

The Unity command-center receives backend WebSocket envelopes (`initial_state`,
`telemetry`, `status`, `health`, `event`, and `device_state`). It displays the
backend's processed state and never becomes a second source of business logic.

## Unity Components

### Core scene layer

- `RescuerController`: CharacterController/Rigidbody-backed movement,
  collision, fall state, and scene spawn/reset.
- `HelmetDigitalTwin`: helmet mesh hierarchy, sensor mounting points, visor
  HUD anchor, LED, buzzer, and vibration visual components.
- `CameraModeController`: switches first-person and command-center cameras
  while preserving player simulation.
- `ScenarioController`: deterministic selection/reset of NORMAL,
  TEMPERATURE_HIGH, CO_HIGH, FALL, SOS, LOW_BATTERY, CONNECTION_LOSS, and
  RECONNECT scenarios.

### Environment layer

- `HazardVolume`: trigger volume with a deterministic intensity profile.
  BuildingFire instances expose temperature and smoke visibility; ConfinedSpaceCO
  instances expose CO and optional temperature.
- `VentilationZone`: reduces CO intensity in its bounds.
- `Obstacle` and `FallZone`: colliders used by Unity physics; FallZone emits a
  local fall input, not a backend safety decision.
- Visual fire/smoke effects are rendering aids only and are explicitly not
  physical gas/fire simulation.

### Device layer

- `TemperatureSensorAdapter`, `CoSensorAdapter`, `ImuSensorAdapter`, and
  `BatterySimulator` sample Unity state and hazard volumes deterministically.
- `LocalSafetyEvaluator` applies the existing thresholds only: temperature
  warning/critical 50/60, CO warning/critical 50/100, low battery <=20, SOS
  critical, and fall critical. Immobility remains aligned with the current
  backend behaviour.
- `VirtualActuatorController` maps NORMAL to GREEN/OFF/OFF, WARNING to
  YELLOW/OFF/OFF, and CRITICAL to RED/ON/ON. It runs even when MQTT is disabled
  or disconnected.
- `MqttDevicePublisher` serializes validated telemetry/status/health payloads
  at configured intervals, tracks connection state, and retries safely.

### Presentation layer

- First-person visor HUD: device ID, temperature, CO, risk, battery, Wi-Fi,
  MQTT state, and actuator state.
- Command-center overlay: external view, current device state from FastAPI
  WebSocket, active alerts, and connection indication.
- All risk/severity labels include text; colours supplement rather than convey
  meaning alone.

## Local Fail-Safe Behaviour

Sensor evaluation and actuator changes happen before any network action.
When MQTT is unavailable, Unity continues sampling, evaluates local safety,
and visibly applies RED/ON/ON for a CRITICAL result. It does not pretend to
deliver messages during the outage and does not add a persistent offline queue.
On reconnect it resumes normal periodic publishing with current values.

Backend offline detection remains authoritative for Dashboard OFFLINE/ONLINE
state. Unity does not implement a competing device-offline decision.

## Configuration

Unity configuration is externalized for device ID, broker host/port, publish
intervals, deterministic random seed, initial battery, and connection-loss
duration. Development defaults target local Mosquitto, but a Unity process
outside Docker uses an address reachable from its host rather than the Docker
service name.

## Testing and Acceptance

Use Unity Test Framework:

- Edit-mode: DTO/schema mapping, topic construction, hazard sensor values,
  threshold parity, actuator mapping, and MQTT-disabled behaviour.
- Play-mode: scene load, hazard entry/exit, fall, first-/third-person camera
  switching, local actuator response while disconnected, and reconnect
  publishing resume.
- Integration: run a Unity scene against Mosquitto/FastAPI, verify backend
  persistence/WebSocket/React dashboard receive valid telemetry, status,
  health, and a Temperature High event path.

Existing backend, Python-simulator, frontend, and Docker tests remain part of
regression validation. Unity-specific tests do not require the existing Python
simulator to be active.

## Delivery Sequence

1. Scaffold a Unity LTS project and document supported editor/package versions.
2. Implement shared C# DTOs, MQTT transport, deterministic virtual sensors,
   local safety, actuator visual state, and edit-mode tests.
3. Build the reusable rescuer/helmet prefab and first-person/command-center
   camera controller.
4. Build BuildingFire and ConfinedSpaceCO scenes from reusable hazard volumes.
5. Add scenario controls, play-mode tests, and an end-to-end local runbook.

Each step is independently runnable. No existing M1-M10 service is removed or
reworked as part of this work.

## Open Decisions Resolved

- Viewpoints: both first-person helmet/visor and command-center.
- Environments: both building fire/smoke and confined-space CO.
- Fidelity: physics-consistent training simulation, not scientific CFD/fire
  modelling.
- Architecture: independent Unity publisher/consumer that reuses the existing
  MQTT and WebSocket contracts.
