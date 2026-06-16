from __future__ import annotations

from typing import Optional

import psycopg
from psycopg.rows import dict_row

from .settings import settings

IntegrityError = psycopg.IntegrityError


def get_conn(include_db: bool = True) -> psycopg.Connection:
    if include_db and settings.database_url:
        return psycopg.connect(
            settings.database_url,
            autocommit=True,
            row_factory=dict_row,
        )
    database: Optional[str] = settings.postgres_db if include_db else settings.postgres_admin_db
    return psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        user=settings.postgres_user,
        password=settings.postgres_password,
        dbname=database,
        autocommit=True,
        row_factory=dict_row,
    )
