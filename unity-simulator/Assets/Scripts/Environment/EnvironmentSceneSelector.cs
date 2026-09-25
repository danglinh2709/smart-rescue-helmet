namespace SmartRescueHelmet.Unity.Environment
{
    public enum RescueEnvironment
    {
        BuildingFire,
        ConfinedSpaceCo,
    }

    public static class EnvironmentSceneSelector
    {
        public static RescueEnvironment FromSceneName(string sceneName)
        {
            return sceneName == "ConfinedSpaceCO"
                ? RescueEnvironment.ConfinedSpaceCo
                : RescueEnvironment.BuildingFire;
        }

        public static string SceneNameFor(RescueEnvironment environment)
        {
            return environment == RescueEnvironment.ConfinedSpaceCo
                ? "ConfinedSpaceCO"
                : "BuildingFire";
        }
    }
}
