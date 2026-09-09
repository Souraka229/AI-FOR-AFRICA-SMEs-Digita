from datetime import datetime

from fastapi import FastAPI

app = FastAPI(
    title="Afrosite Agents Service",
    description="LangGraph agents orchestration service",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "agents",
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("afrosite_agents.main:app", host="0.0.0.0", port=8001, reload=True)
