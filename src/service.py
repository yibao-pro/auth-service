from __future__ import annotations

from typing import Dict, Optional
from uuid import uuid4

from .auth_jwt import create_access_token, hash_password, verify_password
from .db import IntegrityError
from .repo import auth_repo


class UserAlreadyExists(Exception):
    """Raised when a username already exists."""


class AuthService:
    def __init__(self) -> None:
        self.repo = auth_repo

    def register(self, username: str, password: str) -> Dict[str, str]:
        user_id = str(uuid4())
        password_hash = hash_password(password)
        try:
            self.repo.create_user(user_id, username, password_hash)
        except IntegrityError as exc:
            raise UserAlreadyExists from exc
        return {"user_id": user_id, "username": username}

    def login(self, username: str, password: str) -> Optional[Dict[str, str]]:
        record = self.repo.get_user_by_username(username)
        if not record or not verify_password(password, record["password_hash"]):
            return None
        token = create_access_token(record["user_id"], record["username"])
        return {"token": token, "user_id": record["user_id"], "username": record["username"]}


auth_service = AuthService()
