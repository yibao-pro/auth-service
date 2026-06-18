from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, constr


class RegisterRequest(BaseModel):
    username: constr(strip_whitespace=True, min_length=1, max_length=64) = Field(
        ..., description="Unique username, max 64 characters"
    )
    password: constr(min_length=6, max_length=128) = Field(
        ..., description="Password with minimum 6 characters"
    )


class LoginRequest(RegisterRequest):
    """Login shares the same shape as register."""


class AuthResponse(BaseModel):
    status: Literal["success"]
    request_id: str
    user_id: str
    token: Optional[str] = None
    username: Optional[str] = None


class MeResponse(BaseModel):
    status: Literal["success"]
    request_id: str
    user_id: str
    username: str


class TokenRequest(BaseModel):
    token: constr(strip_whitespace=True, min_length=1) = Field(..., description="Bearer token")
