from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request


def _base_url() -> str:
    host = os.getenv("AUTH_SERVICE_TEST_HOST", "127.0.0.1")
    port = os.getenv("AUTH_SERVICE_PORT", "8004")
    return f"http://{host}:{port}"


def _request(method: str, path: str, payload: dict | None = None, token: str | None = None) -> dict:
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(
        url=f"{_base_url()}{path}",
        data=body,
        headers=headers,
        method=method,
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _wait_for_healthz() -> None:
    last_error: Exception | None = None
    for _ in range(30):
        try:
            body = _request("GET", "/healthz")
            if body.get("status") == "success":
                return
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
        time.sleep(1)
    raise RuntimeError(f"service healthz failed: {last_error}")


def main() -> None:
    _wait_for_healthz()

    username = f"ci_auth_{int(time.time())}"
    password = "secret123"

    register_body = _request(
        "POST",
        "/auth/register",
        {"username": username, "password": password},
    )
    assert register_body["status"] == "success"
    assert register_body["user_id"]

    login_body = _request(
        "POST",
        "/auth/login",
        {"username": username, "password": password},
    )
    assert login_body["status"] == "success"
    assert login_body["username"] == username
    token = login_body["token"]
    assert token

    me_body = _request("GET", "/auth/me", token=token)
    assert me_body["status"] == "success"
    assert me_body["username"] == username

    print("ci smoke test passed")


if __name__ == "__main__":
    main()
