using UnityEngine;

namespace SmartRescueHelmet.Unity.Rescue
{
    public enum VictimState
    {
        Waiting,
        Assisted,
        Evacuated,
    }

    public sealed class RescueVictim : MonoBehaviour
    {
        [Min(0.1f)] public float FollowDistance = 1.25f;
        [Min(0.1f)] public float FollowSpeed = 2.5f;

        public VictimState State { get; private set; } = VictimState.Waiting;
        public Transform Rescuer { get; private set; }

        public bool TryAssist(Transform rescuer)
        {
            if (State != VictimState.Waiting || rescuer == null) return false;
            Rescuer = rescuer;
            State = VictimState.Assisted;
            return true;
        }

        public bool Evacuate()
        {
            if (State != VictimState.Assisted) return false;
            State = VictimState.Evacuated;
            Rescuer = null;
            gameObject.SetActive(false);
            return true;
        }

        private void Update()
        {
            if (State != VictimState.Assisted || Rescuer == null) return;
            var followPosition = Rescuer.position - Rescuer.forward * FollowDistance;
            followPosition.y = transform.position.y;
            transform.position = Vector3.MoveTowards(transform.position, followPosition, FollowSpeed * Time.deltaTime);
        }
    }
}
