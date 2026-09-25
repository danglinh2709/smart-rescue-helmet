using UnityEngine;

namespace SmartRescueHelmet.Unity.Player
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class RescuerController : MonoBehaviour
    {
        public float MoveSpeed = 3.5f;
        public float Gravity = -18f;
        public float TurnSpeed = 110f;
        private CharacterController _controller;
        private float _verticalVelocity;
        private void Awake() { _controller = GetComponent<CharacterController>(); }
        private void Update()
        {
            var turn = Input.GetAxisRaw("Horizontal") == 0f ? (Input.GetKey(KeyCode.Q) ? -1f : Input.GetKey(KeyCode.E) ? 1f : 0f) : 0f;
            if (Input.GetKey(KeyCode.LeftArrow)) turn = -1f;
            if (Input.GetKey(KeyCode.RightArrow)) turn = 1f;
            transform.Rotate(0f, turn * TurnSpeed * Time.deltaTime, 0f);
            var input = new Vector3(Input.GetAxisRaw("Horizontal"), 0f, Input.GetAxisRaw("Vertical")).normalized;
            _verticalVelocity = _controller.isGrounded ? -1f : _verticalVelocity + Gravity * Time.deltaTime;
            _controller.Move((transform.TransformDirection(input) * MoveSpeed + Vector3.up * _verticalVelocity) * Time.deltaTime);
        }
    }
}
