from __future__ import annotations

from pathlib import Path

from src.db import get_conn


def main() -> None:
    schema_path = Path(__file__).resolve().parents[1] / "database" / "auth_postgres.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)
    print("auth database schema initialized")


if __name__ == "__main__":
    main()
