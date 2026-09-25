using NUnit.Framework;
using SmartRescueHelmet.Unity.Rescue;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Tests.EditMode
{
    public sealed class RescueMissionTests
    {
        [Test]
        public void Mission_timeout_is_reached_when_elapsed_time_meets_the_limit()
        {
            Assert.That(RescueMission.HasTimedOut(120f, 120f), Is.True);
            Assert.That(RescueMission.HasTimedOut(119.9f, 120f), Is.False);
        }

        [Test]
        public void Mission_completes_only_after_every_registered_victim_is_evacuated()
        {
            var missionObject = new GameObject("Mission");
            var firstObject = new GameObject("FirstVictim");
            var secondObject = new GameObject("SecondVictim");
            var rescuerObject = new GameObject("Rescuer");
            try
            {
                var mission = missionObject.AddComponent<RescueMission>();
                var first = firstObject.AddComponent<RescueVictim>();
                var second = secondObject.AddComponent<RescueVictim>();
                mission.Register(first);
                mission.Register(second);
                first.TryAssist(rescuerObject.transform);
                first.Evacuate();

                Assert.That(mission.EvacuatedCount, Is.EqualTo(1));
                Assert.That(mission.IsComplete, Is.False);

                second.TryAssist(rescuerObject.transform);
                second.Evacuate();

                Assert.That(mission.EvacuatedCount, Is.EqualTo(2));
                Assert.That(mission.IsComplete, Is.True);
            }
            finally
            {
                Object.DestroyImmediate(missionObject);
                Object.DestroyImmediate(firstObject);
                Object.DestroyImmediate(secondObject);
                Object.DestroyImmediate(rescuerObject);
            }
        }
    }
}
