using UnityEngine;

namespace SmartRescueHelmet.Unity.Rescue
{
    public sealed class RescueVictimMarker : MonoBehaviour
    {
        public RescueVictim Victim;
        public Renderer MarkerRenderer;
        public Light MarkerLight;

        public static Color ColorFor(VictimState state)
        {
            return state == VictimState.Assisted ? Color.yellow : Color.red;
        }

        private void Update()
        {
            if (Victim == null || Victim.State == VictimState.Evacuated) return;
            transform.Rotate(0f, 100f * Time.deltaTime, 0f, Space.World);
            var color = ColorFor(Victim.State);
            if (MarkerRenderer != null) MarkerRenderer.material.color = color;
            if (MarkerLight != null) MarkerLight.color = color;
        }
    }
}
