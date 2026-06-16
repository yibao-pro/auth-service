from __future__ import annotations

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.errors import error_response
from src.logging import configure_logging, generate_request_id
from src.routes import router as auth_router
from src.settings import settings


configure_logging()

app = FastAPI(
    title="Auth Service",
    version="0.1.0",
    description="Standalone authentication service for Yibao",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(api_router, prefix=settings.api_prefix)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = generate_request_id(request)
    details = exc.errors()
    if details:
        first = details[0]
        location = ".".join(str(item) for item in first.get("loc", []) if item not in {"body"})
        message = f"{location or 'body'}: {first.get('msg', 'invalid value')}"
    else:
        message = "invalid request body"
    body = error_response(request_id, message, errors=details)
    return JSONResponse(status_code=422, content=body)


@app.middleware("http")
async def allow_private_network(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response


@app.get("/healthz")
async def healthz(request: Request) -> dict:
    request_id = generate_request_id(request)
    return {
        "status": "success",
        "request_id": request_id,
        "service": "auth-service",
        "port": settings.auth_service_port,
        "message": "ok",
    }
