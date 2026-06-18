from __future__ import annotations

from concurrent import futures
from typing import Callable

import grpc
from grpc import StatusCode
from grpc_health.v1 import health, health_pb2, health_pb2_grpc
from pydantic import ValidationError

from src.auth_jwt import get_current_user_from_token
from src.generated import auth_pb2, auth_pb2_grpc
from src.logging import configure_logging, generate_request_id, logger
from src.schemas import LoginRequest, RegisterRequest, TokenRequest
from src.service import UserAlreadyExists, auth_service
from src.settings import settings

SERVICE_NAME = "auth.v1.AuthService"


class AuthServiceServicer(auth_pb2_grpc.AuthServiceServicer):
    def _abort(self, context: grpc.ServicerContext, code: StatusCode, message: str, request_id: str) -> None:
        context.set_trailing_metadata((("x-request-id", request_id),))
        context.abort(code, message)

    def Healthz(self, request: auth_pb2.HealthzRequest, context: grpc.ServicerContext) -> auth_pb2.HealthzResponse:
        request_id = generate_request_id()
        return auth_pb2.HealthzResponse(
            status="success",
            request_id=request_id,
            service="auth-service",
            port=settings.auth_service_port,
            message="ok",
        )

    def Register(
        self, request: auth_pb2.RegisterRequest, context: grpc.ServicerContext
    ) -> auth_pb2.AuthResponse:
        request_id = generate_request_id(self._metadata_getter(context))
        try:
            payload = RegisterRequest(username=request.username, password=request.password)
            record = auth_service.register(payload.username, payload.password)
        except ValidationError as exc:
            self._abort(context, StatusCode.INVALID_ARGUMENT, self._first_validation_error(exc), request_id)
        except UserAlreadyExists:
            self._abort(context, StatusCode.ALREADY_EXISTS, "username already exists", request_id)
        return auth_pb2.AuthResponse(status="success", request_id=request_id, user_id=record["user_id"])

    def Login(self, request: auth_pb2.LoginRequest, context: grpc.ServicerContext) -> auth_pb2.AuthResponse:
        request_id = generate_request_id(self._metadata_getter(context))
        try:
            payload = LoginRequest(username=request.username, password=request.password)
        except ValidationError as exc:
            self._abort(context, StatusCode.INVALID_ARGUMENT, self._first_validation_error(exc), request_id)
        token = auth_service.login(payload.username, payload.password)
        if not token:
            self._abort(context, StatusCode.UNAUTHENTICATED, "invalid credentials", request_id)
        return auth_pb2.AuthResponse(
            status="success",
            request_id=request_id,
            token=token["token"],
            user_id=token["user_id"],
            username=token["username"],
        )

    def Me(self, request: auth_pb2.MeRequest, context: grpc.ServicerContext) -> auth_pb2.MeResponse:
        request_id = generate_request_id(self._metadata_getter(context))
        try:
            payload = TokenRequest(token=request.token)
            current_user = get_current_user_from_token(payload.token)
        except ValidationError as exc:
            self._abort(context, StatusCode.INVALID_ARGUMENT, self._first_validation_error(exc), request_id)
        except ValueError as exc:
            self._abort(context, StatusCode.UNAUTHENTICATED, str(exc), request_id)
        return auth_pb2.MeResponse(
            status="success",
            request_id=request_id,
            user_id=current_user["user_id"],
            username=current_user["username"],
        )

    @staticmethod
    def _first_validation_error(exc: ValidationError) -> str:
        details = exc.errors()
        if not details:
            return "invalid request"
        first = details[0]
        location = ".".join(str(item) for item in first.get("loc", []))
        return f"{location or 'request'}: {first.get('msg', 'invalid value')}"

    @staticmethod
    def _metadata_getter(context: grpc.ServicerContext) -> Callable[[str], str | None]:
        metadata = {key.lower(): value for key, value in context.invocation_metadata()}

        def get_value(key: str) -> str | None:
            return metadata.get(key.lower())

        return get_value


def build_server() -> grpc.Server:
    configure_logging()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthServiceServicer(), server)

    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
    health_servicer.set(SERVICE_NAME, health_pb2.HealthCheckResponse.SERVING)
    health_servicer.set("grpc.health.v1.Health", health_pb2.HealthCheckResponse.SERVING)

    listen_addr = f"{settings.auth_service_host}:{settings.auth_service_port}"
    server.add_insecure_port(listen_addr)
    logger.info("starting auth-service grpc server on %s", listen_addr)
    return server


def serve() -> None:
    server = build_server()
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
