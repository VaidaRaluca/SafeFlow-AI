from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies.database import get_db


router = APIRouter(prefix="/api/test", tags=["Test"])


@router.get("/db")
def test_db_connection(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"database_result": result.scalar()}


@router.get("/models")
def test_sqlalchemy_models(db: Session = Depends(get_db)):
    user_count = db.scalar(text("SELECT count(*) FROM users"))
    account_count = db.scalar(text("SELECT count(*) FROM accounts"))
    transaction_count = db.scalar(text("SELECT count(*) FROM transactions"))

    return {
        "message": "Database tables are reachable",
        "users": user_count,
        "accounts": account_count,
        "transactions": transaction_count,
    }
