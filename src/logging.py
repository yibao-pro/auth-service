from __future__ import annotations

import logging
from typing import Callable, Optional
from uuid import uuid4


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


logger = logging.getLogger("auth-service")


def generate_request_id(header_getter: Optional[Callable[[str], str | None]] = None) -> str:
    if header_getter:
        candidate = header_getter("x-request-id") or header_getter("X-Request-Id")
        if candidate:
            return candidate
    return uuid4().hex
