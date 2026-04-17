from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.database import get_db
from app.auth import get_current_user
from app.models import Follow


router = APIRouter()


@router.post("/follow/{user_id}")
async def follow_user(user_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    existing = await db.execute(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already following this user")

    new_following = Follow(
        follower_id=current_user.id,
        following_id=user_id,
    )
    db.add(new_following)
    await db.commit()
    return {"message": "Followed"}
