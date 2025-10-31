from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.users import UserCreate, UserLogin, UserResponse, Token
from datetime import timedelta
from src.models import users
from src.schemas.users import User as users_schema
from src.utils.response_wrapper import api_response
from src.controllers.middleware.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


router = APIRouter(prefix="/users", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
def register(user_data: users.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(users_schema).filter(users_schema.phone == user_data.phone).first()
    if db_user:
        raise HTTPException(status_code=400,
                             detail="user already exists")

    hashed_password = get_password_hash(user_data.password)

    new_user = users_schema(
        **user_data.model_dump())
    new_user.password = hashed_password
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    new_user.password=""
    
    user_response = UserResponse(**user_data.model_dump(),id=new_user.id) #issue here TODO:
    
    return api_response(data=user_response, message="user registered successfully")


@router.post("/login", response_model=Token)
def login(login_data: users.UserLogin, db: Session = Depends(get_db)):
    db_user = (
        db.query(users_schema)
        .filter((users_schema.phone == login_data.username) | (users_schema.email == login_data.username))
        .first()
    )

    if not db_user or not verify_password(login_data.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": db_user.phone}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    token = Token(access_token=access_token, token_type="bearer")
    return api_response(data=token, message="login successful")