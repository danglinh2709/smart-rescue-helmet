using NUnit.Framework;
using SmartRescueHelmet.Unity.Environment;

namespace SmartRescueHelmet.Unity.Tests.EditMode
{
    public sealed class EnvironmentSceneSelectorTests
    {
        [TestCase("BuildingFire", RescueEnvironment.BuildingFire)]
        [TestCase("ConfinedSpaceCO", RescueEnvironment.ConfinedSpaceCo)]
        [TestCase("Bootstrap", RescueEnvironment.BuildingFire)]
        public void Scene_name_selects_the_expected_rescue_environment(string sceneName, RescueEnvironment expected)
        {
            Assert.That(EnvironmentSceneSelector.FromSceneName(sceneName), Is.EqualTo(expected));
        }

        [TestCase(RescueEnvironment.BuildingFire, "BuildingFire")]
        [TestCase(RescueEnvironment.ConfinedSpaceCo, "ConfinedSpaceCO")]
        public void Rescue_environment_has_a_buildable_scene_name(RescueEnvironment environment, string expected)
        {
            Assert.That(EnvironmentSceneSelector.SceneNameFor(environment), Is.EqualTo(expected));
        }
    }
}
