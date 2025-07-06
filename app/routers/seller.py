from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.models import User, UserRole
from app.dependencies import require_roles

router = APIRouter(prefix="/seller", tags=["Seller"])

@router.get("/dashboard")
def seller_dashboard(current_user: User = Depends(require_roles(UserRole.SELLER))):
    return {"message": f"Welcome Seller {current_user.email}"}
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.dependencies import require_roles
from app.models import UserRole

router = APIRouter(prefix="/seller", tags=["Seller"])

@router.get("/dashboard", summary="Seller-only dashboard")
def seller_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SELLER, UserRole.ADMIN))
):
    return {
        "message": f"Welcome Seller {current_user.email}",
        "role": current_user.role.value
    }
