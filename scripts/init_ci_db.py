from __future__ import annotations

import os
import subprocess
from pathlib import Path

import psycopg
from psycopg import sql


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _connect_admin() -> psycopg.Connection:
    return psycopg.connect(
        host=_env("CI_POSTGRES_HOST", "127.0.0.1"),
        port=int(_env("CI_POSTGRES_PORT", "5432")),
        user=_env("CI_POSTGRES_ADMIN_USER", "postgres"),
        password=_env("CI_POSTGRES_ADMIN_PASSWORD", "postgres"),
        dbname=_env("CI_POSTGRES_ADMIN_DB", "postgres"),
        autocommit=True,
    )


def _connect_target() -> psycopg.Connection:
    return psycopg.connect(
        host=_env("POSTGRES_HOST", "127.0.0.1"),
        port=int(_env("POSTGRES_PORT", "5432")),
        user=_env("POSTGRES_USER", "yibao_user"),
        password=_env("POSTGRES_PASSWORD", "123456"),
        dbname=_env("POSTGRES_DB", "yibao_auth"),
        autocommit=True,
    )


def _ensure_role_and_db() -> None:
    role_name = _env("POSTGRES_USER", "yibao_user")
    role_password = _env("POSTGRES_PASSWORD", "123456")
    db_name = _env("POSTGRES_DB", "yibao_auth")

    try:
        with _connect_admin() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (role_name,))
                if cursor.fetchone() is None:
                    cursor.execute(
                        sql.SQL("CREATE ROLE {} WITH LOGIN PASSWORD {}").format(
                            sql.Identifier(role_name),
                            sql.Literal(role_password),
                        )
                    )

                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
                if cursor.fetchone() is None:
                    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))

                cursor.execute(
                    sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                        sql.Identifier(db_name),
                        sql.Identifier(role_name),
                    )
                )
        return
    except psycopg.Error:
        pass

    try:
        _run_psql_fallback(role_name, role_password, db_name)
        return
    except RuntimeError:
        pass

    try:
        with _connect_target():
            return
    except psycopg.Error as exc:
        raise RuntimeError(
            "failed to initialize postgres role/database via admin connection, psql fallback, and direct target connection"
        ) from exc


def _run_psql_fallback(role_name: str, role_password: str, db_name: str) -> None:
    base_commands = []
    if os.getenv("CI_POSTGRES_ADMIN_DSN"):
        base_commands.append(["psql", os.environ["CI_POSTGRES_ADMIN_DSN"]])
    base_commands.append(["psql", "-d", _env("CI_POSTGRES_ADMIN_DB", "postgres")])
    base_commands.append(["sudo", "-u", "postgres", "psql", "-d", _env("CI_POSTGRES_ADMIN_DB", "postgres")])

    for base in base_commands:
        try:
            role_check = subprocess.run(
                base + ["-At", "-c", f"SELECT 1 FROM pg_roles WHERE rolname = '{role_name}';"],
                check=True,
                capture_output=True,
                text=True,
            )
            if role_check.stdout.strip() != "1":
                subprocess.run(
                    base
                    + [
                        "-v",
                        "ON_ERROR_STOP=1",
                        "-c",
                        f"CREATE ROLE {role_name} WITH LOGIN PASSWORD '{role_password}';",
                    ],
                    check=True,
                )

            db_check = subprocess.run(
                base + ["-At", "-c", f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';"],
                check=True,
                capture_output=True,
                text=True,
            )
            if db_check.stdout.strip() != "1":
                subprocess.run(
                    base + ["-v", "ON_ERROR_STOP=1", "-c", f'CREATE DATABASE "{db_name}";'],
                    check=True,
                )

            subprocess.run(
                base + ["-v", "ON_ERROR_STOP=1", "-c", f'GRANT ALL PRIVILEGES ON DATABASE "{db_name}" TO {role_name};'],
                check=True,
            )
            return
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    raise RuntimeError("failed to initialize postgres role/database via admin connection and psql fallback")


def _apply_schema() -> None:
    role_name = _env("POSTGRES_USER", "yibao_user")
    schema_path = Path(__file__).resolve().parents[1] / "database" / "auth_postgres.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")

    with _connect_target() as conn:
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)
            cursor.execute(
                sql.SQL("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {}").format(
                    sql.Identifier(role_name)
                )
            )
            cursor.execute(
                sql.SQL("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {}").format(
                    sql.Identifier(role_name)
                )
            )
            cursor.execute(
                sql.SQL(
                    "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {}"
                ).format(sql.Identifier(role_name))
            )
            cursor.execute(
                sql.SQL(
                    "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {}"
                ).format(sql.Identifier(role_name))
            )


def main() -> None:
    _ensure_role_and_db()
    _apply_schema()
    print("ci database init passed")


if __name__ == "__main__":
    main()
