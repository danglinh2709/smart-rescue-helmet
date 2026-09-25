using SmartRescueHelmet.Unity.Bootstrap;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Editor
{
    public static class SceneBuilder
    {
        public static void CreateBootstrapScene()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            new GameObject("RuntimeBootstrap").AddComponent<RuntimeBootstrap>();
            EditorSceneManager.SaveScene(scene, "Assets/Scenes/Bootstrap.unity");
        }
    }
}
