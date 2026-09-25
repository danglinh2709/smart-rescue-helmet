using UnityEngine;

namespace SmartRescueHelmet.Unity.Rescue
{
    [RequireComponent(typeof(Collider))]
    public sealed class SafeZone : MonoBehaviour
    {
        private void Awake() => GetComponent<Collider>().isTrigger = true;

        public bool TryEvacuate(RescueVictim victim)
        {
            return victim != null && victim.Evacuate();
        }

        private void OnTriggerEnter(Collider other)
        {
            var victim = other.GetComponent<RescueVictim>();
            if (victim != null) TryEvacuate(victim);
        }
    }
}
