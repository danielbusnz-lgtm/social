from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, exists, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.auth import get_current_user
from app.database import get_db
from app.models import Follow, Like, Post, User
from app.schemas import PostCreate, PostResponse

router = APIRouter()


def _post_query(current_user_id: int):
    like_count = (
        select(func.count(Like.id)).where(Like.post_id == Post.id).correlate(Post).scalar_subquery()
    )
    liked_by_me = exists(
        select(1).where(Like.post_id == Post.id, Like.user_id == current_user_id)
    ).correlate(Post)
    return select(
        Post,
        User.username,
        like_count.label("like_count"),
        liked_by_me.label("liked_by_me"),
    ).join(User, Post.author_id == User.id)


@router.get("/users/{username}/posts", response_model=list[PostResponse])
async def user_posts(username: str, db=Depends(get_db), current_user=Depends(get_current_user)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    rows = await db.execute(
        _post_query(current_user.id)
        .where(Post.author_id == user.id)
        .order_by(Post.created_at.desc())
    )
    return [
        PostResponse(
            id=post.id,
            content=post.content,
            username=username,
            created_at=post.created_at,
            like_count=like_count,
            liked_by_me=liked_by_me,
        )
        for post, username, like_count, liked_by_me in rows.all()
    ]


@router.post("/posts")
async def create_post(post: PostCreate, db=Depends(get_db), current_user=Depends(get_current_user)):

    new_post = Post(
        author_id=current_user.id,
        content=post.content,
    )

    db.add(new_post)
    await db.commit()
    return {"message": "Content Published"}


@router.get("/me/posts", response_model=list[PostResponse])
async def my_posts(db=Depends(get_db), current_user=Depends(get_current_user)):
    rows = await db.execute(
        _post_query(current_user.id)
        .where(Post.author_id == current_user.id)
        .order_by(Post.created_at.desc())
    )
    return [
        PostResponse(
            id=post.id,
            content=post.content,
            username=username,
            created_at=post.created_at,
            like_count=like_count,
            liked_by_me=liked_by_me,
        )
        for post, username, like_count, liked_by_me in rows.all()
    ]


@router.get("/feed", response_model=list[PostResponse])
async def show_feed(db=Depends(get_db), current_user=Depends(get_current_user)):
    result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == current_user.id)
    )
    following_ids = result.scalars().all()

    author_ids = list(following_ids) + [current_user.id]

    rows = await db.execute(
        _post_query(current_user.id)
        .where(Post.author_id.in_(author_ids))
        .order_by(Post.created_at.desc())
    )
    return [
        PostResponse(
            id=post.id,
            content=post.content,
            username=username,
            created_at=post.created_at,
            like_count=like_count,
            liked_by_me=liked_by_me,
        )
        for post, username, like_count, liked_by_me in rows.all()
    ]


@router.post("/posts/{post_id}/like", status_code=204)
async def like_post(post_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    post = await db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    stmt = (
        pg_insert(Like)
        .values(user_id=current_user.id, post_id=post_id)
        .on_conflict_do_nothing(index_elements=["user_id", "post_id"])
    )
    await db.execute(stmt)
    await db.commit()


@router.delete("/posts/{post_id}/like", status_code=204)
async def unlike_post(post_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    await db.execute(delete(Like).where(Like.user_id == current_user.id, Like.post_id == post_id))
    await db.commit()
