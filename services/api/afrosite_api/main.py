import os
from datetime import UTC, datetime

import uvicorn
from fastapi import FastAPI

from afrosite_api.auth.router import router as auth_router
from afrosite_api.catalog.router import router as catalog_router
from afrosite_api.ledger.router import router as ledger_router
from afrosite_api.orders.router import router as orders_router
from afrosite_api.payments.router import router as payments_router
from afrosite_api.tenants.router import router as tenants_router

app = FastAPI(
    title="Afrosite API",
    description="Backend API Service for Afrosite Platform",
    version="0.1.0",
)
app.include_router(auth_router)
app.include_router(tenants_router)
app.include_router(catalog_router)
app.include_router(orders_router)
app.include_router(ledger_router)
app.include_router(payments_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "api",
        "timestamp": datetime.now(UTC).isoformat(),
    }


if __name__ == "__main__":
    # Local reload only; containers/deploy bind via process manager (HOST/PORT).
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("afrosite_api.main:app", host=host, port=port, reload=True)
