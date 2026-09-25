using UnityEngine;
using UnityEngine.SceneManagement;

namespace SmartRescueHelmet.Unity.Environment
{
    public sealed class RescueSceneNavigator : MonoBehaviour
    {
        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.F1))
                SceneManager.LoadScene(EnvironmentSceneSelector.SceneNameFor(RescueEnvironment.BuildingFire));
            if (Input.GetKeyDown(KeyCode.F2))
                SceneManager.LoadScene(EnvironmentSceneSelector.SceneNameFor(RescueEnvironment.ConfinedSpaceCo));
        }
    }
}
