from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.auth import register_user_with_role


from app.database import get_db
from app import models, schemas, auth
from app.schemas import UserCreate, UserRole

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/register/user", response_model=schemas.User, summary="Register a normal user")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return auth.register_user_with_role(user, db, UserRole.USER)

@router.post("/register/seller", response_model=schemas.User)
def register_seller(user: UserCreate, db: Session = Depends(get_db)):
    return register_user_with_role(user, db, UserRole.SELLER)

@router.post("/register/admin", response_model=schemas.User, summary="Register an admin")
def register_admin(user: UserCreate, db: Session = Depends(get_db)):
    return auth.register_user_with_role(user, db, UserRole.admin)

@router.post("/login", summary="Login user")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = auth.create_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
