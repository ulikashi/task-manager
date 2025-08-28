from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import User, Role
from ..security import get_password_hash, verify_password

async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    res = await session.execute(select(User).where(User.email == email))
    return res.scalar_one_or_none()

async def create_user(session: AsyncSession, *, email: str, password: str, full_name: str | None = None, role: Role = Role.user) -> User:
    user = User(email=email, hashed_password=get_password_hash(password), full_name=full_name, role=role)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def authenticate(session: AsyncSession, *, email: str, password: str) -> User | None:
    user = await get_user_by_email(session, email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None