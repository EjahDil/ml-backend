from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm

from models.model import User
from schemas.schema import UserCreate, Token
from controllers.middleware.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
)
from db.database import get_session

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=dict)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    # Check if username already exists
    user_exists = session.exec(select(User).where(User.username == user_data.username)).first()
    if user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    # Map is_admin bool to role string
    # role = "admin" if user_data.is_admin else "user"

    # Always assign role as "user" regardless of user_data input
    role = "user"

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=role
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message": "User registered successfully"}



# @router.post("/login", response_model=Token)
# def login(
#     form_data: OAuth2PasswordRequestForm = Depends(), 
#     session: Session = Depends(get_session)
# ):
#     user = session.exec(select(User).where(User.username == form_data.username)).first()
    
#     if not user or not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, 
#             detail="Invalid username or password"
#         )

#     # Build access token
#     access_token = create_access_token(
#         data={"sub": user.username}, 
#         expires_delta=timedelta(minutes=30)
#     )

#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user": {
#             "id": user.id,
#             "username": user.username,
#             "email": user.email,
#             "is_admin": user.is_admin
#         }
#     }


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    # Build access token
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=30)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role.value
        }
    }
