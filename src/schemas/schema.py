from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# User schemas

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str  

class User(UserBase):
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: Optional[str]

    class Config:
       from_attributes= True 


# Token schemas

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


class UserRead(UserBase):
    id: int
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
    user_id: int
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



# Pydantic schema for model creation

class MLModelCreate(BaseModel):
    name: str
    description: Optional[str] = None


class PredictionRead(BaseModel):
    id: int
    input_data: str
    prediction: int
    probability: float
    created_at: Optional[datetime]

    class Config:
        from_attributes= True