from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt
from passlib.context import CryptContext
from uuid import uuid4
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def _create_token(subject: str, *, token_type: str, expires_delta: timedelta, secret: str) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    jti = uuid4().hex
    to_encode = {"sub": subject, "type": token_type, "exp": int(expire.timestamp()), "iat": int(now.timestamp()), "jti": jti}
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt, jti

def create_access_token(subject: str) -> str:
    token, _ = _create_token(
        subject,
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        secret=settings.JWT_SECRET_KEY,
    )
    return token

def create_refresh_token(subject: str) -> tuple[str, str, datetime]:
    expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token, jti = _create_token(
        subject,
        token_type="refresh",
        expires_delta=expires,
        secret=settings.JWT_REFRESH_SECRET_KEY,
    )
    exp_dt = datetime.now(timezone.utc) + expires
    return token, jti, exp_dt

def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

def decode_refresh_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])