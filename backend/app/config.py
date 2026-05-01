import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://dan:social123@localhost:5432/social")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
JWT_SECRET = os.getenv("JWT_SECRET", "some-random-secret-key")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
