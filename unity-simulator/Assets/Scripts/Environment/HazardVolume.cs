using UnityEngine;

namespace SmartRescueHelmet.Unity.Environment
{
    [RequireComponent(typeof(Collider))]
    public sealed class HazardVolume : MonoBehaviour
    {
        [Min(0)] public float TemperatureDelta;
        [Min(0)] public float CoPpm;
        private void Awake() { GetComponent<Collider>().isTrigger = true; }
        private void Reset() { GetComponent<Collider>().isTrigger = true; }
        public bool Contains(Vector3 position) => GetComponent<Collider>().bounds.Contains(position);
    }
}
