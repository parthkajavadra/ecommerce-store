# app/dependencies.py
from fastapi import Depends, HTTPException, status
from app.auth import get_current_user
from app.models import User, UserRole

def require_roles(*roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access requires one of: {[r.value for r in roles]}"
            )
        return current_user
    return role_checker
