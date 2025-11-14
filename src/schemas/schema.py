from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID

# User schemas

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    # is_admin: bool

    @field_validator("confirm_password")
    def passwords_match(cls, v, info):
        password = info.data.get("password")
        if password != v:
            raise ValueError("Passwords do not match")
        return v


class User(UserBase):
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str


class UserOut(BaseModel):
    id: UUID
    username: str
    full_name: str | None = None
    role: str
    created_at: datetime

    class Config:
        from_attributes= True 

# Token schemas

class UserLoginResponse(BaseModel):
    username: str
    full_name: Optional[str]
    role: str 

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserLoginResponse

class TokenData(BaseModel):
    username: Optional[str] = None


class UserRead(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes= True 

class FeedbackCreate(BaseModel):
    prediction_id: int
    correct: Optional[bool] = None
    comment: Optional[str] = None


class FeedbackRead(BaseModel):
    id: int
    prediction_id: int
    user_id: UUID
    correct: Optional[bool]
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes= True


class MLModelRead(BaseModel):
    id: int
    name: str
    version: str
    description: Optional[str]
    created_at: Optional[str]

    class Config:
        from_attributes= True


class UserNameRoleResponse(BaseModel):
    username: str
    role: str



# Pydantic schema for model creation

class MLModelCreate(BaseModel):
    name: str
    description: Optional[str] = None


class PredictionRead(BaseModel):
    id: int
    input_data: str
    prediction: int
    probability: float
    external_customer_id: Optional[str] = None
    created_at: Optional[datetime]

    class Config:
        from_attributes= True


class CurrentUser(BaseModel):
    id: Optional[str] = None

class PredictionRequest(BaseModel):
    customer_id: str
    data: Dict
    current_user: Optional[CurrentUser] = None