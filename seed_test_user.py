import asyncio
from sqlalchemy import select
from app.db.session import async_session_factory
from app.models.user import User
from app.api.deps import create_access_token

# pwd_context removed

async def seed_user():
    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.username == "testuser"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                username="testuser",
                email="test@example.com",
                hashed_password="dummy_hash",
                display_name="Test User",
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print("User created.")
        else:
            print("User already exists.")
        
        token = create_access_token(user.id, user.username)
        print(f"TEST_TOKEN={token}")

if __name__ == "__main__":
    asyncio.run(seed_user())
