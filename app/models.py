from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func, ForeignKey
from datetime import datetime


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_info"

    id: Mapped[int] = mapped_column(primary_key = True)
    username: Mapped[str] = mapped_column(String(30), unique = True)
    hashed_password: Mapped[str]  = mapped_column(String(255))
    email_address: Mapped[str] = mapped_column(String(40), unique = True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default= func.now())


class Post(Base):
    __tablename__  = 'post'

    id: Mapped[int] = mapped_column(primary_key = True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user_info.id"))
    content: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default= func.now())


class Follow(Base):
    __tablename__ = 'follow'

    id: Mapped[int] = mapped_column(primary_key = True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("user_info.id"))
    following_id: Mapped[int] = mapped_column(ForeignKey("user_info.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default = func.now())
