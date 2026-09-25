using NUnit.Framework;
using SmartRescueHelmet.Unity.Environment;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Tests.EditMode
{
    public sealed class HazardVolumeTests
    {
        [Test]
        public void Runtime_hazard_volume_configures_its_collider_as_a_trigger()
        {
            var zone = GameObject.CreatePrimitive(PrimitiveType.Cube);
            try
            {
                zone.AddComponent<HazardVolume>();

                Assert.That(zone.GetComponent<Collider>().isTrigger, Is.True);
            }
            finally
            {
                Object.DestroyImmediate(zone);
            }
        }
    }
}
