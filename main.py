from __future__ import annotations

from src.settings import settings


def main() -> None:
    print("auth-service build smoke check passed")
    print("transport=grpc")
    print(f"port={settings.auth_service_port}")


if __name__ == "__main__":
    main()
