from __future__ import annotations

import logging
from typing import Optional
from uuid import uuid4

from fastapi import Request


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def generate_request_id(request: Optional[Request] = None) -> str:
    if request:
        candidate = request.headers.get("x-request-id") or request.headers.get("X-Request-Id")
        if candidate:
            return candidate
    return uuid4().hex
