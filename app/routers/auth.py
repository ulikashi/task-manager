from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone
from ..database import get_async_session
from ..schemas import UserCreate, UserOut, TokenPair, RefreshRequest
from ..models import User, RefreshToken
from ..crud.users import create_user, authenticate
from ..security import create_access_token, create_refresh_token, decode_refresh_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup", response_model=TokenPair, status_code=201, summary="Register a new user")
async def signup(payload: UserCreate, session: AsyncSession = Depends(get_async_session)):
    exists = await session.execute(select(User).where(User.email == payload.email))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await create_user(session, email=payload.email, password=payload.password, full_name=payload.full_name)
    access = create_access_token(str(user.id))
    refresh, jti, exp_dt = create_refresh_token(str(user.id))
    session.add(RefreshToken(user_id=user.id, jti=jti, expires_at=exp_dt))
    await session.commit()
    return TokenPair(access_token=access, refresh_token=refresh)

@router.post("/login", response_model=TokenPair, summary="Login and get tokens")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_async_session)):
    user = await authenticate(session, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access = create_access_token(str(user.id))
    refresh, jti, exp_dt = create_refresh_token(str(user.id))
    session.add(RefreshToken(user_id=user.id, jti=jti, expires_at=exp_dt))
    await session.commit()
    return TokenPair(access_token=access, refresh_token=refresh)

@router.post("/refresh", response_model=TokenPair, summary="Rotate refresh token and get a new access token")
async def refresh(payload: RefreshRequest, session: AsyncSession = Depends(get_async_session)):
    try:
        data = decode_refresh_token(payload.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = int(data["sub"]) if data.get("sub") else None
    jti = data.get("jti")
    if not user_id or not jti:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    res = await session.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    db_token = res.scalar_one_or_none()
    if not db_token or db_token.revoked:
        raise HTTPException(status_code=401, detail="Refresh token revoked or not found")
    if db_token.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    db_token.revoked = True
    access = create_access_token(str(user_id))
    new_refresh, new_jti, exp_dt = create_refresh_token(str(user_id))
    session.add(RefreshToken(user_id=user_id, jti=new_jti, expires_at=exp_dt))
    await session.commit()
    return TokenPair(access_token=access, refresh_token=new_refresh)

@router.post("/logout", status_code=204, summary="Revoke all refresh tokens for the current user")
async def logout(payload: RefreshRequest, session: AsyncSession = Depends(get_async_session)):
    try:
        data = decode_refresh_token(payload.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = int(data["sub"]) if data.get("sub") else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    await session.execute(
        update(RefreshToken).where(RefreshToken.user_id == user_id).values(revoked=True)
    )
    await session.commit()
    return None