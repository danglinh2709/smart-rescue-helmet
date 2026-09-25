using SmartRescueHelmet.Unity.Devices;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Environment
{
    [RequireComponent(typeof(Collider))]
    public sealed class FallZone : MonoBehaviour
    {
        public HelmetDeviceController Device;
        private void Reset() { GetComponent<Collider>().isTrigger = true; }
        private void OnTriggerEnter(Collider other)
        {
            if (Device != null && other.GetComponent<CharacterController>() != null) Device.ReportFall();
        }
    }
}
