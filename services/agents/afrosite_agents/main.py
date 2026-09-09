import os
from datetime import UTC, datetime

import uvicorn
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
        "timestamp": datetime.now(UTC).isoformat(),
    }


if __name__ == "__main__":
    # Local reload only; containers/deploy bind via process manager (HOST/PORT).
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run("afrosite_agents.main:app", host=host, port=port, reload=True)
