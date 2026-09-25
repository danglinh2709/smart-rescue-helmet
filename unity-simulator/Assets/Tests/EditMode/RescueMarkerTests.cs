using NUnit.Framework;
using SmartRescueHelmet.Unity.Rescue;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Tests.EditMode
{
    public sealed class RescueMarkerTests
    {
        [Test]
        public void Marker_color_distinguishes_waiting_and_assisted_victims()
        {
            Assert.That(RescueVictimMarker.ColorFor(VictimState.Waiting), Is.EqualTo(Color.red));
            Assert.That(RescueVictimMarker.ColorFor(VictimState.Assisted), Is.EqualTo(Color.yellow));
        }
    }
}
