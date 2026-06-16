from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from .auth_jwt import get_current_user
from .errors import error_response
from .logging import generate_request_id
from .schemas import AuthResponse, LoginRequest, MeResponse, RegisterRequest
from .service import UserAlreadyExists, auth_service

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, request: Request) -> dict:
    request_id = generate_request_id(request)
    token = auth_service.login(payload.username, payload.password)
    if not token:
        error = error_response(request_id, "invalid credentials")
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=error)
    return AuthResponse(
        status="success",
        request_id=request_id,
        token=token["token"],
        user_id=token["user_id"],
        username=token["username"],
    ).model_dump()


@router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterRequest, request: Request) -> dict:
    request_id = generate_request_id(request)
    try:
        record = auth_service.register(payload.username, payload.password)
    except UserAlreadyExists:
        error = error_response(request_id, "username already exists")
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=error)
    return AuthResponse(status="success", request_id=request_id, user_id=record["user_id"]).model_dump()


@router.get("/me", response_model=MeResponse)
async def me(request: Request, current_user: dict = Depends(get_current_user)) -> dict:
    request_id = generate_request_id(request)
    return MeResponse(
        status="success",
        request_id=request_id,
        user_id=current_user["user_id"],
        username=current_user["username"],
    ).model_dump()
