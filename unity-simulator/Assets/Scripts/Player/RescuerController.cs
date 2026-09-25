using SmartRescueHelmet.Unity.Rescue;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Player
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class RescuerController : MonoBehaviour
    {
        public float MoveSpeed = 3.5f;
        public float Gravity = -18f;
        public float TurnSpeed = 110f;
        [Min(.1f)] public float InteractionRange = 2f;
        public RescueVictim NearbyVictim { get; private set; }
        private CharacterController _controller;
        private float _verticalVelocity;
        private void Awake() { _controller = GetComponent<CharacterController>(); }
        private void Update()
        {
            NearbyVictim = FindNearestWaitingVictim();
            if (Input.GetKeyDown(KeyCode.F)) TryAssistNearestVictim();
            var turn = Input.GetAxisRaw("Horizontal") == 0f ? (Input.GetKey(KeyCode.Q) ? -1f : Input.GetKey(KeyCode.E) ? 1f : 0f) : 0f;
            if (Input.GetKey(KeyCode.LeftArrow)) turn = -1f;
            if (Input.GetKey(KeyCode.RightArrow)) turn = 1f;
            transform.Rotate(0f, turn * TurnSpeed * Time.deltaTime, 0f);
            var input = new Vector3(Input.GetAxisRaw("Horizontal"), 0f, Input.GetAxisRaw("Vertical")).normalized;
            _verticalVelocity = _controller.isGrounded ? -1f : _verticalVelocity + Gravity * Time.deltaTime;
            _controller.Move((transform.TransformDirection(input) * MoveSpeed + Vector3.up * _verticalVelocity) * Time.deltaTime);
        }

        public bool TryAssistNearestVictim()
        {
            NearbyVictim = FindNearestWaitingVictim();
            return NearbyVictim != null && NearbyVictim.TryAssist(transform);
        }

        private RescueVictim FindNearestWaitingVictim()
        {
            RescueVictim nearest = null;
            var nearestDistance = InteractionRange;
            foreach (var victim in Object.FindObjectsByType<RescueVictim>(FindObjectsSortMode.None))
            {
                if (victim.State != VictimState.Waiting) continue;
                var distance = Vector3.Distance(transform.position, victim.transform.position);
                if (distance <= nearestDistance)
                {
                    nearest = victim;
                    nearestDistance = distance;
                }
            }
            return nearest;
        }
    }
}
