from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.users import UserResponse # UserCreate, UserLogin, UserResponse, Token
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
import bcrypt

from datetime import timedelta
from src.models import users
from src.schemas.users import User as users_schema
from src.utils.response_wrapper import api_response


router = APIRouter(prefix="/users", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__default_rounds=12, deprecated="auto")

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



def get_password_hash(password):  
    password = password[:72].encode('utf-8')
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    return hashed.decode('utf-8')
