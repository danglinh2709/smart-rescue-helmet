using NUnit.Framework;
using SmartRescueHelmet.Unity.Player;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Tests.EditMode
{
    public sealed class CommandCenterCameraFollowTests
    {
        [Test]
        public void Desired_position_uses_the_target_offset()
        {
            var target = new Vector3(2f, 1f, -3f);
            var offset = new Vector3(8f, 6f, -8f);

            Assert.That(CommandCenterCameraFollow.DesiredPosition(target, offset), Is.EqualTo(target + offset));
        }
    }
}
