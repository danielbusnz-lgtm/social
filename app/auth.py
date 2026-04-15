from passlib.context import CryptContext
from jose import jwt
from fastapi import Depends, HTTPException
from sqlalchemy import select
from datetime import datetime, timedelta

from app.config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_db
from app.models import User



pwd_context = CryptContext(schemes=["bcrypt"])


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password:str, hash_password):
    return pwd_context.verify(password, hash_password)


def create_token(user_id):
    data= {"sub": user_id, "exp": datetime.now( ) + timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)}
    token = jwt.encode(data,JWT_SECRET , algorithm=JWT_ALGORITHM) 
    return token

async def get_current_user(token: str, db= Depends(get_db)):
    data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
    user_id  = data["sub"]
    
    sql_result = await db.execute(select(User).where(User.id==  user_id))
   
    user = sql_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code =401, detail = "User not found")
    return user
