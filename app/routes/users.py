from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.schemas import UserLogin, UserRegister
from app.database import get_db
from app.auth import create_token, hash_password, verify_password
from app.models import User


router = APIRouter()


@router.post("/register")
async def register_user(user: UserRegister, db=Depends(get_db)):
    find_user_email = await db.execute(select(User).where(User.email_address == user.email))
    if find_user_email.scalar():
        raise HTTPException(status_code=400, detail="User already exists")

    find_username = await db.execute(select(User).where(User.username == user.username))
    if find_username.scalar():
        raise HTTPException(status_code= 400, detail= " Username Already Taken")


    new_user = User(
        username=user.username,
        email_address=user.email,
        hashed_password=hash_password(user.password),
    )
    try:

        db.add(new_user)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code = 400, detail = "USername or Email Already Taken")
    return {"message": "User registered"}


@router.post("/login")
async def login_user(user: UserLogin, db = Depends(get_db)):

    result = await db.execute(select(User).where(User.username == user.username))
    found_user =  result.scalar_one_or_none()
    if not found_user:
        raise HTTPException(status_code = 401, detail = "Invalid Credentials")
    if not verify_password(user.password, found_user.hashed_password):
        raise HTTPException(status_code =401, detail = "Invalid Credentials")
    token = create_token(found_user.id)
    return {"access_token": token}
