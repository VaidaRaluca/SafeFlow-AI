from fastapi import FastAPI

from app.api.routes.accounts import router as accounts_router
from app.api.routes.auth import router as auth_router
from app.api.routes.payments import router as payments_router
from app.api.routes.transactions import router as transactions_router

app = FastAPI(
    title="SafeFlow AI Backend",
    version="0.1.0"
)

app.include_router(auth_router, prefix="/auth")
app.include_router(accounts_router, prefix="/api/accounts")
app.include_router(payments_router)
app.include_router(transactions_router)
