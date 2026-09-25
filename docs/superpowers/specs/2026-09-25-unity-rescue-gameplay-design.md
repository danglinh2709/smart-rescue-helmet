# Unity Rescue Gameplay Design

## Goal

Add a playable rescue loop to the Unity simulator: locate a victim, assist them, escort them to a safe zone, and show mission progress without changing the existing MQTT or safety contracts.

## Scope

- One controllable rescuer remains `RescuerHelmet` / FF03.
- Two virtual victims are spawned in each environment, represented with clear procedural humanoid primitives.
- A rescuer within interaction distance presses `F` to assist a victim. The victim follows at a safe offset.
- Entering a Safe Zone with an assisted victim evacuates that victim.
- Mission succeeds after all victims are evacuated.
- HUD shows victim count, interaction prompt, and completion state.

## Boundaries

Gameplay is local Unity state. It does not modify MQTT telemetry schemas, Backend APIs, WebSocket payloads, Safety Engine thresholds, or Dashboard data.

## State Model

`VictimState` is `Waiting`, `Assisted`, or `Evacuated`. `RescueMission` owns the victim list and derives `EvacuatedCount` and `IsComplete`. `SafeZone` transitions an assisted victim to `Evacuated` only once.

## Error Handling

Missing references are ignored safely. A victim cannot follow more than one rescuer and an evacuated victim cannot be assisted again.

## Verification

EditMode tests cover assistance, follow eligibility, evacuation, duplicate prevention, and mission completion. Manual Play Mode verifies `F` interaction and escorting to the marked Safe Zone.
