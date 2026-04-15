# Social Media Backend — MVP Design

## User Journeys

1. **New user signs up**
   - `POST /register` (username, email, password)
   - Gets back their user info

2. **User logs in**
   - `POST /login` (username, password)
   - Gets back a JWT token

3. **User creates a post**
   - `POST /posts` (content + token)
   - Post saved to database

4. **User views their feed**
   - `GET /feed` (token)
   - Sees posts from people they follow, newest first

5. **User follows someone**
   - `POST /follow/{user_id}` (token)
   - Now sees their posts in feed

6. **User unfollows someone**
   - `DELETE /follow/{user_id}` (token)
   - No longer sees their posts

7. **User views a profile**
   - `GET /users/{user_id}`
   - Sees their info + their posts

## Data Models

### User
- id
- username (unique)
- email (unique)
- hashed_password
- created_at

### Post
- id
- author_id → User
- content
- created_at

### Follow
- id
- follower_id → User (the one doing the following)
- following_id → User (the one being followed)
- created_at

## Relationships
- A user has many posts
- A user can follow many users
- A user can be followed by many users
- Feed = all posts where author_id is in the list of people you follow

## Tech Stack
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- python-jose + passlib (JWT auth)
- uvicorn
