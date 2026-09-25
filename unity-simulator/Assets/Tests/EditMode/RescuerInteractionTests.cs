using NUnit.Framework;
using SmartRescueHelmet.Unity.Player;
using SmartRescueHelmet.Unity.Rescue;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Tests.EditMode
{
    public sealed class RescuerInteractionTests
    {
        [Test]
        public void Rescuer_assists_the_nearest_waiting_victim_in_range()
        {
            var rescuerObject = new GameObject("Rescuer");
            var victimObject = new GameObject("Victim");
            try
            {
                var rescuer = rescuerObject.AddComponent<RescuerController>();
                rescuer.InteractionRange = 2f;
                victimObject.transform.position = new Vector3(1f, 0f, 0f);
                var victim = victimObject.AddComponent<RescueVictim>();

                Assert.That(rescuer.TryAssistNearestVictim(), Is.True);
                Assert.That(victim.State, Is.EqualTo(VictimState.Assisted));
            }
            finally
            {
                Object.DestroyImmediate(victimObject);
                Object.DestroyImmediate(rescuerObject);
            }
        }
    }
}
