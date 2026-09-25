using NUnit.Framework;
using SmartRescueHelmet.Unity.Rescue;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Tests.EditMode
{
    public sealed class RescueVictimTests
    {
        [Test]
        public void Waiting_victim_can_be_assisted_once()
        {
            var victimObject = new GameObject("Victim");
            var rescuerObject = new GameObject("Rescuer");
            try
            {
                var victim = victimObject.AddComponent<RescueVictim>();

                Assert.That(victim.TryAssist(rescuerObject.transform), Is.True);
                Assert.That(victim.State, Is.EqualTo(VictimState.Assisted));
                Assert.That(victim.TryAssist(rescuerObject.transform), Is.False);
            }
            finally
            {
                Object.DestroyImmediate(victimObject);
                Object.DestroyImmediate(rescuerObject);
            }
        }

        [Test]
        public void Assisted_victim_can_be_evacuated_once()
        {
            var victimObject = new GameObject("Victim");
            var rescuerObject = new GameObject("Rescuer");
            try
            {
                var victim = victimObject.AddComponent<RescueVictim>();
                victim.TryAssist(rescuerObject.transform);

                Assert.That(victim.Evacuate(), Is.True);
                Assert.That(victim.State, Is.EqualTo(VictimState.Evacuated));
                Assert.That(victim.Evacuate(), Is.False);
            }
            finally
            {
                Object.DestroyImmediate(victimObject);
                Object.DestroyImmediate(rescuerObject);
            }
        }
    }
}
