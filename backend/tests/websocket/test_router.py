from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_websocket_endpoint_accepts_client_and_returns_initial_state() -> None:
    from app.websocket.router import manager, router

    manager.clear()
    app = FastAPI()
    app.include_router(router)

    with TestClient(app) as client:
        with client.websocket_connect("/ws") as websocket:
            assert websocket.receive_json() == {
                "type": "initial_state",
                "data": [],
            }

    assert manager.connection_count == 0
