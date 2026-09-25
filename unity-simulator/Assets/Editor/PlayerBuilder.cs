using UnityEditor;
using UnityEditor.Build.Reporting;

namespace SmartRescueHelmet.Unity.Editor
{
    public static class PlayerBuilder
    {
        public static void BuildBootstrapWindows()
        {
            BuildPipeline.BuildPlayer(new[] { "Assets/Scenes/Bootstrap.unity" }, "Build/SmartRescueHelmet.exe", BuildTarget.StandaloneWindows64, BuildOptions.None);
        }
    }
}
