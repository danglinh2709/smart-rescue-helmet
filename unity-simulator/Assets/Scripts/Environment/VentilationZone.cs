using UnityEngine;

namespace SmartRescueHelmet.Unity.Environment
{
    [RequireComponent(typeof(Collider))]
    public sealed class VentilationZone : MonoBehaviour
    {
        [Range(0f, 1f)] public float CoReduction = .8f;
        private void Awake() { GetComponent<Collider>().isTrigger = true; }
        public bool Contains(Vector3 position) => GetComponent<Collider>().bounds.Contains(position);
    }
}
