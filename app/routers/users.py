from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..deps import get_current_user, get_current_admin
from ..schemas import UserOut
from ..models import User
from ..database import get_async_session

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=UserOut)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/", response_model=list[UserOut])
async def list_users(
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(get_current_admin),
):
    res = await session.execute(select(User).order_by(User.id))
    return list(res.scalars().all())