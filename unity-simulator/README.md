# SMART RESCUE HELMET — Unity 3D Simulator

Unity 6 project for the software-first rescue training prototype. It publishes
the existing MQTT contract as device `FF03`; FastAPI remains responsible for
validation, safety events, persistence, WebSocket, and the React dashboard.

## Open and run

1. In Unity Hub, open this directory: `D:\Class\smart-rescue-helmet\unity-simulator`.
2. Open one of the scenes under `Assets/Scenes/`:
   - `BuildingFire.unity`: heat/fire/smoke environment.
   - `ConfinedSpaceCO.unity`: CO hazard and ventilation environment.
3. Press Play. The local broker must be available at `localhost:1883`.

## Controls

- `W`, `A`, `S`, `D`: move
- `Q`/`E` or arrow keys: turn
- `C`: switch helmet visor and command-center cameras
- `1`: normal/reset
- `2`: fall
- `3`: SOS
- `4`: low battery
- `5`: simulate MQTT publishing loss
- `6`: resume publishing
- `7`: temperature-high scenario (Building Fire)
- `8`: CO-high scenario (Confined Space)
- `F1`: load Building Fire
- `F2`: load Confined Space CO

## Safety boundary

The environment and local virtual actuators are a training simulation, not a
certified fire, smoke, CO dispersion, or real rescue decision system. Local
LED/buzzer/vibration state reacts before MQTT publishing, so it continues to
change while publishing is disabled.
