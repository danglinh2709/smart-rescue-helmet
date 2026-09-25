using UnityEngine;

namespace SmartRescueHelmet.Unity.Player
{
    public sealed class CameraModeController : MonoBehaviour
    {
        public Camera FirstPersonCamera;
        public Camera CommandCenterCamera;
        public bool IsCommandCenter { get; private set; }
        private void Start() { SetCommandCenter(false); }
        private void Update() { if (Input.GetKeyDown(KeyCode.C)) SetCommandCenter(!IsCommandCenter); }
        public void SetCommandCenter(bool enabled)
        {
            IsCommandCenter = enabled;
            if (FirstPersonCamera != null) FirstPersonCamera.enabled = !enabled;
            if (CommandCenterCamera != null) CommandCenterCamera.enabled = enabled;
        }
    }
}
