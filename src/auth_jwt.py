from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext

from .settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except ValueError:
        return False


def create_access_token(user_id: str, username: str) -> str:
    now = datetime.now(tz=timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": user_id,
        "username": username,
        "iat": now.timestamp(),
        "exp": expire.timestamp(),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


def get_current_user_from_token(token: str) -> Dict[str, str]:
    if not token:
        raise ValueError("missing token")
    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise ValueError("invalid token") from exc
    user_id = payload.get("sub")
    username = payload.get("username")
    if not user_id or not username:
        raise ValueError("invalid token payload")
    return {"user_id": user_id, "username": username}
