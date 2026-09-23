import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.telemetry import router as telemetry_router
from app.api.event import router as event_router
from app.api.health import router as health_router

from app.database.init_db import init_database
from app.mqtt.subscriber import start_subscriber
from app.services.device_state import devices


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo các bảng trong PostgreSQL
    init_database()

    # Khởi động MQTT Subscriber
    mqtt_task = asyncio.create_task(start_subscriber())

    yield

    # Dừng MQTT Subscriber
    mqtt_task.cancel()

    try:
        await mqtt_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Smart Rescue Helmet Backend",
    version="0.4.0",
    lifespan=lifespan,
)

# Đăng ký các Router
app.include_router(telemetry_router)
app.include_router(event_router)
app.include_router(health_router)


# ==========================
# BASIC API
# ==========================

@app.get("/")
def read_root():
    return {
        "service": "smart-rescue-helmet-backend",
        "status": "running",
    }


@app.get("/health")
def read_health():
    return {
        "status": "ok",
    }


@app.get("/api/v1/devices")
def get_runtime_devices():
    return {
        "count": len(devices),
        "devices": devices,
    }