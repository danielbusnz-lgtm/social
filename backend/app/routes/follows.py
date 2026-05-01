"""Follow and unfollow endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Follow, User

router = APIRouter()

DbDep = Annotated[AsyncSession, Depends(get_db)]
UserDep = Annotated[User, Depends(get_current_user)]


@router.delete("/follow/{user_id}", status_code=204)
async def unfollow_user(user_id: int, db: DbDep, current_user: UserDep) -> None:
    """Unfollow a user.

    Raises:
        HTTPException: 404 if the current user is not following user_id.
    """
    existing = await db.execute(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_id,
        )
    )
    if not existing.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Not following this user")

    await db.execute(
        delete(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_id,
        )
    )
    await db.commit()


@router.post("/follow/{user_id}")
async def follow_user(user_id: int, db: DbDep, current_user: UserDep) -> dict:
    """Follow a user.

    Raises:
        HTTPException: 400 if trying to follow yourself or already following.
    """
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
