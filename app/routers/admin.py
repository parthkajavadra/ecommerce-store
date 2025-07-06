from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.database import get_db
from app.models import User
from app.dependencies import require_roles
from app.schemas import UserRole

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard", summary="Admin-only dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    return {
        "message": f"Welcome Admin {current_user.email}",
        "role": current_user.role.value
    }
