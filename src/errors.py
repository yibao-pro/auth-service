from __future__ import annotations

from typing import Any, Dict


def error_response(request_id: str, detail: str, **payload: Any) -> Dict[str, Any]:
    body = {"status": "error", "request_id": request_id, "message": detail}
    body.update(payload)
    return body
