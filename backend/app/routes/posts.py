from fastapi import APIRouter, Depends
from sqlalchemy import select
from app.schemas import PostCreate
from app.database import get_db
from app.auth import get_current_user
from app.models import Post, Follow


router = APIRouter()


@router.post("/posts")
async def create_post(post: PostCreate, db=Depends(get_db), current_user=Depends(get_current_user)):


    new_post = Post(
    author_id = current_user.id,
    content=post.content,
    )

    db.add(new_post)
    await db.commit()
    return {"message": "Content Published"}

@router.get("/feed")
async def show_feed(db=Depends(get_db), current_user=Depends(get_current_user)):
    result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == current_user.id)
    )
    following_ids = result.scalars().all()

    posts = await db.execute(
        select(Post).where(Post.author_id.in_(following_ids)).order_by(Post.created_at.desc())
    )
    return posts.scalars().all()
