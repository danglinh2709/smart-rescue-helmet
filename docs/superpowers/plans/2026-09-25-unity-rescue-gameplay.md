# Unity Rescue Gameplay Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provide a playable local rescue mission with victims, assistance, following, evacuation, and HUD progress.

**Architecture:** Local gameplay components live under `Assets/Scripts/Rescue`. Victims own only their local state; `RescueMission` tracks aggregate progress; `SafeZone` owns evacuation transitions. `RuntimeBootstrap` constructs scene-specific objects and the HUD reads the mission.

**Tech Stack:** Unity 6, C#, NUnit EditMode tests.

**Spec:** `docs/superpowers/specs/2026-09-25-unity-rescue-gameplay-design.md`

## Global Constraints

- Do not change MQTT topics, JSON contracts, Backend APIs, Safety Engine thresholds, or Dashboard behavior.
- Use procedural Unity primitives; do not add third-party assets or packages.
- Keep rescue state local to Unity in this phase.

---

### Task 1: Victim state and assistance

**Files:**
- Create: `unity-simulator/Assets/Scripts/Rescue/RescueVictim.cs`
- Create: `unity-simulator/Assets/Tests/EditMode/RescueVictimTests.cs`

**Interfaces:**
- Produces `VictimState`, `RescueVictim.TryAssist(Transform)`, `RescueVictim.Evacuate()`.

- [ ] Write tests for successful assistance, rejected re-assistance, and evacuation.
- [ ] Run Unity EditMode tests and observe the tests fail because `RescueVictim` does not exist.
- [ ] Implement the smallest victim state machine to make those tests pass.
- [ ] Re-run the tests.

### Task 2: Mission and Safe Zone

**Files:**
- Create: `unity-simulator/Assets/Scripts/Rescue/RescueMission.cs`
- Create: `unity-simulator/Assets/Scripts/Rescue/SafeZone.cs`
- Create: `unity-simulator/Assets/Tests/EditMode/RescueMissionTests.cs`

**Interfaces:**
- Consumes `RescueVictim`.
- Produces `RescueMission.EvacuatedCount`, `RescueMission.IsComplete`, and `SafeZone.TryEvacuate`.

- [ ] Write tests for one evacuation and all-victims mission completion.
- [ ] Run tests and observe expected failure.
- [ ] Implement mission registration and idempotent evacuation.
- [ ] Re-run tests.

### Task 3: Runtime construction and player interaction

**Files:**
- Modify: `unity-simulator/Assets/Scripts/Bootstrap/RuntimeBootstrap.cs`
- Modify: `unity-simulator/Assets/Scripts/Player/RescuerController.cs`

**Interfaces:**
- Consumes `RescueVictim`, `RescueMission`, `SafeZone`.
- Produces `RescuerController.NearbyVictim` and `TryAssistNearbyVictim()` via `F`.

- [ ] Add a focused edit-mode test for interaction range.
- [ ] Run it and observe failure.
- [ ] Spawn victims and safe zone using primitives; implement nearest-victim assistance and follow movement.
- [ ] Re-run tests and verify Play Mode manually.

### Task 4: HUD and manual verification

**Files:**
- Modify: `unity-simulator/Assets/Scripts/Presentation/VisorHudController.cs`
- Modify: `unity-simulator/README.md`

- [ ] Show objective, interaction prompt, evacuation count, and completion text.
- [ ] Document `F` interaction and safe-zone objective.
- [ ] Compile Unity and manually validate rescue in both scenes.
