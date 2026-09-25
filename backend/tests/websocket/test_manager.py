import asyncio

import pytest


class FakeWebSocket:
    def __init__(self, fail_on_send: bool = False) -> None:
        self.accepted = False
        self.fail_on_send = fail_on_send
        self.messages: list[dict[str, object]] = []

    async def accept(self) -> None:
        self.accepted = True

    async def send_json(self, message: dict[str, object]) -> None:
        if self.fail_on_send:
            raise RuntimeError("closed connection")
        self.messages.append(message)


def load_manager_module():
    try:
        from app.websocket.manager import ConnectionManager
        from app.websocket.schemas import build_realtime_message
    except ModuleNotFoundError as exc:
        pytest.fail(f"WebSocket realtime modules are not implemented: {exc}")
    return ConnectionManager, build_realtime_message


def test_connect_sends_initial_state_and_disconnect_cleans_up() -> None:
    ConnectionManager, _ = load_manager_module()
    manager = ConnectionManager()
    socket = FakeWebSocket()

    async def exercise() -> None:
        await manager.connect(socket)
        await manager.send_initial_state(socket, [{"device_id": "FF01"}])
        manager.disconnect(socket)

    asyncio.run(exercise())

    assert socket.accepted is True
    assert socket.messages == [
        {
            "type": "initial_state",
            "data": [{"device_id": "FF01"}],
        }
    ]
    assert manager.connection_count == 0


@pytest.mark.parametrize("message_type", ["telemetry", "status", "health", "event"])
def test_broadcast_delivers_each_realtime_message_type(message_type: str) -> None:
    ConnectionManager, build_realtime_message = load_manager_module()
    manager = ConnectionManager()
    socket = FakeWebSocket()
    message = build_realtime_message(
        message_type,
        device_id="FF01",
        timestamp="2026-09-24T10:00:00+00:00",
        data={"value": 1},
    )

    async def exercise() -> None:
        await manager.connect(socket)
        await manager.broadcast(message)

    asyncio.run(exercise())

    assert socket.messages[-1] == message


def test_multiple_clients_receive_broadcast_when_one_connection_fails() -> None:
    ConnectionManager, build_realtime_message = load_manager_module()
    manager = ConnectionManager()
    healthy = FakeWebSocket()
    broken = FakeWebSocket(fail_on_send=True)
    message = build_realtime_message(
        "device_state",
        device_id="FF01",
        timestamp="2026-09-24T10:00:00+00:00",
        data={"device_id": "FF01", "device_status": "ONLINE"},
    )

    async def exercise() -> None:
        await manager.connect(healthy)
        await manager.connect(broken)
        await manager.broadcast(message)

    asyncio.run(exercise())

    assert healthy.messages[-1] == message
    assert manager.connection_count == 1


def test_serializer_keeps_internal_values_json_safe() -> None:
    _, build_realtime_message = load_manager_module()

    message = build_realtime_message(
        "telemetry",
        device_id="FF01",
        timestamp="2026-09-24T10:00:00+00:00",
        data={"internal": object()},
    )

    assert message["type"] == "telemetry"
    assert isinstance(message["data"], dict)
