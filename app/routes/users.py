from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.schemas import UserLogin, UserRegister
from app.database import get_db
from app.auth import create_token, get_current_user, hash_password, verify_password
from app.models import User, Post, Follow
from app.schemas import PostCreate


router = APIRouter()


@router.post("/register")
async def register_user(user: UserRegister, db=Depends(get_db)):
    find_user = await db.execute(select(User).where(User.email_address == user.email))
    if find_user.scalar():
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        username=user.username,
        email_address=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
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


@router.post("/post")
async def create_post(post: PostCreate, db=Depends(get_db), current_user=Depends(get_current_user)):
  

    new_post = Post(
    author_id = current_user.id,
    content=post.content,
    )

    db.add(new_post)
    await db.commit()
    return {"message": "Content Published"}

@router.post("/follow/{user_id}")
async def follow_user(user_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    new_following = Follow(
        follower_id=current_user.id,
        following_id=user_id,
    )
    db.add(new_following)
    await db.commit()
    return {"message": "Followed"}


