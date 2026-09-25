# Unity-to-Platform Integration Runbook

This runbook verifies the full local data path using Unity device `FF03`.
It is a training/prototype verification, not a hardware certification.

## Preconditions

From the repository root, start the stack:

```powershell
docker compose up -d postgres mosquitto backend frontend
Invoke-WebRequest -UseBasicParsing http://localhost:8000/health
```

Expected health body:

```json
{"status":"ok"}
```

Open `unity-simulator` with Unity 6.6.3f1. Open either
`Assets/Scenes/BuildingFire.unity` or `Assets/Scenes/ConfinedSpaceCO.unity`.
Press Play. Unity publishes to the local anonymous development broker at
`localhost:1883` using device ID `FF03`.

## Assertion 1 — normal telemetry reaches the platform

1. Play `BuildingFire` and leave the rescuer at spawn.
2. Observe MQTT from a second terminal:

```powershell
docker compose exec mosquitto mosquitto_sub -h localhost -t "helmet/FF03/#" -v
```

3. Expected topics:

```text
helmet/FF03/telemetry
helmet/FF03/status
helmet/FF03/health
```

4. Confirm the Unity HUD shows `BACKEND WS: CONNECTED` followed by a message
type such as `telemetry` or `device_state`.
5. Open `http://localhost:5173` and confirm FF03 appears in the dashboard.

Pass conditions: `risk_level` is `NORMAL`, temperature is approximately 31 C,
CO is approximately 5 ppm, and actuator is GREEN/OFF/OFF.

## Assertion 2 — temperature high event

1. With `BuildingFire` running, press `7`.
2. Unity must show local `CRITICAL` and LED/buzzer/vibration indicators active.
3. MQTT telemetry must contain a temperature at or above 60 C.
4. The backend creates a `TEMPERATURE_HIGH` event with `CRITICAL` severity.
5. Dashboard and Unity command-center state update without page reload.

Verify persistence with the existing API endpoints or database query after
observing the WebSocket update. The backend safety engine, not Unity, is the
authority that creates the event.

## Assertion 3 — CO high event and ventilation

1. Press `F2` to load `ConfinedSpaceCO`.
2. Press `8` to place the rescuer in the CO hazard.
3. Expected telemetry CO is at or above 100 ppm, local risk is `CRITICAL`, and
the backend emits `CO_HIGH` with `CRITICAL` severity.
4. Move to the blue ventilation zone to observe a deterministic CO reduction.

## Assertion 4 — fail-safe while publishing is lost

1. Press `5` to disable Unity MQTT publishing.
2. Press `7` in BuildingFire or `8` in ConfinedSpaceCO.
3. Unity local actuator must still be RED/ON/ON.
4. No new MQTT message is expected while publishing is disabled.
5. Press `6` to resume publishing; normal periodic telemetry/status/health
must resume.

## Evidence to record

For each run, record UTC/local time, scene, scenario key, one MQTT payload,
one backend API/WebSocket observation, and whether the dashboard listed FF03.
Do not record secrets or credentials. Local anonymous MQTT is development-only;
production must use authentication and TLS.
