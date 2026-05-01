from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select

from app.auth import create_token, get_current_user, hash_password, verify_password
from app.database import get_db
from app.models import Follow, Post, User
from app.schemas import UserLogin, UserRegister

router = APIRouter()


@router.get("/users/{username}")
async def get_user(
    username: str, db=Depends(get_db), current_user=Depends(get_current_user)
):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    post_count_result = await db.execute(
        select(func.count()).select_from(Post).where(Post.author_id == user.id)
    )
    post_count = post_count_result.scalar_one()

    follower_count_result = await db.execute(
        select(func.count()).select_from(Follow).where(Follow.following_id == user.id)
    )
    follower_count = follower_count_result.scalar_one()

    following_count_result = await db.execute(
        select(func.count()).select_from(Follow).where(Follow.follower_id == user.id)
    )
    following_count = following_count_result.scalar_one()

    follow_check = await db.execute(
        select(func.count())
        .select_from(Follow)
        .where(
            Follow.follower_id == current_user.id,
            Follow.following_id == user.id,
        )
    )
    is_followed_by_me = follow_check.scalar_one() > 0

    return {
        "id": user.id,
        "username": user.username,
        "created_at": user.created_at,
        "post_count": post_count,
        "follower_count": follower_count,
        "following_count": following_count,
        "is_followed_by_me": is_followed_by_me,
    }


@router.get("/me")
async def get_me(db=Depends(get_db), current_user=Depends(get_current_user)):
    count_result = await db.execute(
        select(func.count()).select_from(Post).where(Post.author_id == current_user.id)
    )
    post_count = count_result.scalar_one()
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email_address,
        "created_at": current_user.created_at,
        "post_count": post_count,
    }


@router.post("/register")
async def register_user(user: UserRegister, db=Depends(get_db)):
    find_user_email = await db.execute(
        select(User).where(User.email_address == user.email)
    )
    if find_user_email.scalar():
        raise HTTPException(status_code=400, detail="User already exists")

    find_username = await db.execute(select(User).where(User.username == user.username))
    if find_username.scalar():
        raise HTTPException(status_code=400, detail=" Username Already Taken")

    new_user = User(
        username=user.username,
        email_address=user.email,
        hashed_password=hash_password(user.password),
    )
    try:

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="USername or Email Already Taken")
    token = create_token(new_user.id)
    return {"access_token": token}


@router.post("/login")
async def login_user(user: UserLogin, db=Depends(get_db)):

    result = await db.execute(select(User).where(User.username == user.username))
    found_user = result.scalar_one_or_none()
    if not found_user:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    if not verify_password(user.password, found_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    token = create_token(found_user.id)
    return {"access_token": token}
