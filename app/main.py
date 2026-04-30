from fastapi import FastAPI

from app.api.routes.payments import router as payments_router
from app.api.routes.test_router import router as test_router

app = FastAPI(
    title="SafeFlow AI Backend",
    version="0.1.0"
)

app.include_router(payments_router)
app.include_router(test_router)


for route in app.routes:
    print(route.path)
