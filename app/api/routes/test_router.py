from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, select

from app.dependencies.database import get_db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction


router = APIRouter(prefix="/api/test", tags=["Test"])


@router.get("/db")
def test_db_connection(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"database_result": result.scalar()}


@router.get("/models")
def test_sqlalchemy_models(db: Session = Depends(get_db)):
    user_count = db.scalar(select(text("count(*)")).select_from(User.__table__))
    account_count = db.scalar(select(text("count(*)")).select_from(Account.__table__))
    transaction_count = db.scalar(select(text("count(*)")).select_from(Transaction.__table__))

    return {
        "message": "SQLAlchemy models work",
        "users": user_count,
        "accounts": account_count,
        "transactions": transaction_count,
    }