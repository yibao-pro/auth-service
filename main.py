from __future__ import annotations

from api.app import app


def main() -> None:
    print("auth-service build smoke check passed")
    print(f"title={app.title}")
    print(f"version={app.version}")


if __name__ == "__main__":
    main()
