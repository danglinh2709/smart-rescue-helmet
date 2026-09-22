from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "service": "smart-rescue-helmet-backend",
        "status": "running",
    }


@app.get("/health")
def read_health() -> dict[str, str]:
    return {"status": "ok"}
