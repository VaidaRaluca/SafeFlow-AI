from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.account import AccountResponse
from app.services.account_service import AccountService


router = APIRouter(tags=["Accounts"])


@router.get("/me", response_model=AccountResponse)
def get_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountResponse:
    return AccountService(db).get_current_account(current_user.id)
