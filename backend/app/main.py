from fastapi import FastAPI

from app.api.orders import router as orders_router
from app.api.payments import router as payments_router

app = FastAPI(
    title="PaymentService",
    version="0.1.0",
)

app.include_router(orders_router, prefix="/api")
app.include_router(payments_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
