from __future__ import annotations

from typing import Any, Dict, Optional

from .db import get_conn


class AuthRepository:
    def create_user(self, user_id: str, username: str, password_hash: str) -> None:
        with get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (user_id, username, password_hash)
                    VALUES (%s, %s, %s)
                    """,
                    (user_id, username, password_hash),
                )

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        with get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT user_id, username, password_hash
                    FROM users
                    WHERE username=%s
                    LIMIT 1
                    """,
                    (username,),
                )
                return cursor.fetchone()


auth_repo = AuthRepository()
