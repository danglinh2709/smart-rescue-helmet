using UnityEngine;

namespace SmartRescueHelmet.Unity.Player
{
    public sealed class CommandCenterCameraFollow : MonoBehaviour
    {
        public Transform Target;
        public Vector3 Offset = new Vector3(9f, 7f, -9f);
        [Min(.1f)] public float FollowSpeed = 7f;

        public static Vector3 DesiredPosition(Vector3 targetPosition, Vector3 offset) => targetPosition + offset;

        private void LateUpdate()
        {
            if (Target == null) return;
            var desired = DesiredPosition(Target.position, Offset);
            transform.position = Vector3.Lerp(transform.position, desired, FollowSpeed * Time.deltaTime);
            transform.LookAt(Target.position + Vector3.up * .6f);
        }
    }
}
