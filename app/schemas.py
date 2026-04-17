from pydantic import BaseModel, EmailStr
from datetime import datetime




class UserRegister(BaseModel):
    username: str
    email: EmailStr 
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserRespone(BaseModel):
    id: int
    username: str
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str

class PostCreate(BaseModel):
    content: str


class PostResponse(BaseModel):
    id: int
    content: str
    username: str
    created_at: datetime

    
