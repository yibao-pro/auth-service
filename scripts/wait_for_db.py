from __future__ import annotations

import os
import time

import psycopg


def main() -> None:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        connect_kwargs = {"conninfo": database_url}
    else:
        connect_kwargs = {
            "host": os.getenv("VOICE_APP_POSTGRES_HOST", os.getenv("POSTGRES_HOST", "postgres")),
            "port": int(os.getenv("VOICE_APP_POSTGRES_PORT", os.getenv("POSTGRES_PORT", "5432"))),
            "user": os.getenv("VOICE_APP_POSTGRES_USER", os.getenv("POSTGRES_USER", "yibao_user")),
            "password": os.getenv("VOICE_APP_POSTGRES_PASSWORD", os.getenv("POSTGRES_PASSWORD", "123456")),
            "dbname": os.getenv("VOICE_APP_POSTGRES_DB", os.getenv("POSTGRES_DB", "yibao_auth")),
        }

    deadline = time.time() + int(os.getenv("DB_WAIT_TIMEOUT_SECONDS", "60"))
    while time.time() < deadline:
        try:
            with psycopg.connect(autocommit=True, **connect_kwargs):
                print("database is ready")
                return
        except psycopg.Error:
            time.sleep(1)

    raise SystemExit("database wait timed out")


if __name__ == "__main__":
    main()
