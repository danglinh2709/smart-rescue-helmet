using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Rescue
{
    public sealed class RescueMission : MonoBehaviour
    {
        private readonly List<RescueVictim> _victims = new List<RescueVictim>();
        [Min(30f)] public float TimeLimitSeconds = 180f;

        public int TotalVictims => _victims.Count;
        public int EvacuatedCount => _victims.Count(victim => victim != null && victim.State == VictimState.Evacuated);
        public float ElapsedSeconds { get; private set; }
        public float RemainingSeconds => Mathf.Max(0f, TimeLimitSeconds - ElapsedSeconds);
        public bool IsFailed => HasTimedOut(ElapsedSeconds, TimeLimitSeconds) && EvacuatedCount < TotalVictims;
        public bool IsComplete => TotalVictims > 0 && EvacuatedCount == TotalVictims;

        public static bool HasTimedOut(float elapsedSeconds, float timeLimitSeconds) => elapsedSeconds >= timeLimitSeconds;

        public void Register(RescueVictim victim)
        {
            if (victim != null && !_victims.Contains(victim)) _victims.Add(victim);
        }

        private void Update()
        {
            if (!IsComplete && !IsFailed) ElapsedSeconds += Time.deltaTime;
        }
    }
}
