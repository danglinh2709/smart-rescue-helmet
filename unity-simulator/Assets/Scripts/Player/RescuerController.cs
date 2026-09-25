using UnityEngine;

namespace SmartRescueHelmet.Unity.Player
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class RescuerController : MonoBehaviour
    {
        public float MoveSpeed = 3.5f;
        public float Gravity = -18f;
        private CharacterController _controller;
        private float _verticalVelocity;
        private void Awake() { _controller = GetComponent<CharacterController>(); }
        private void Update()
        {
            var input = new Vector3(Input.GetAxisRaw("Horizontal"), 0f, Input.GetAxisRaw("Vertical")).normalized;
            _verticalVelocity = _controller.isGrounded ? -1f : _verticalVelocity + Gravity * Time.deltaTime;
            _controller.Move((transform.TransformDirection(input) * MoveSpeed + Vector3.up * _verticalVelocity) * Time.deltaTime);
        }
    }
}
