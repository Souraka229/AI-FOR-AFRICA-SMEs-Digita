from datetime import datetime

from fastapi import FastAPI

app = FastAPI(
    title="Afrosite API",
    description="Backend API Service for Afrosite Platform",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "api",
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("afrosite_api.main:app", host="0.0.0.0", port=8000, reload=True)
