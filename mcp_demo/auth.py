from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Awaitable, Callable

from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from mcp_demo.config import DemoSettings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DemoPrincipal:
    client_id: str
    role: str
    scopes: list[str]

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes


class BearerTokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: DemoSettings, protected_prefixes: tuple[str, ...]):
        super().__init__(app)
        self.settings = settings
        self.protected_prefixes = protected_prefixes

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if self._is_public(request.url.path):
            return await call_next(request)

        header_value = request.headers.get(self.settings.auth_header_name, "")
        scheme, _, token = header_value.partition(" ")
        token_details = self.settings.demo_token_catalog.get(token)

        if scheme.lower() != "bearer" or token_details is None:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Missing or invalid bearer token",
                    "hint": "Use Authorization: Bearer <token>",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.principal = DemoPrincipal(
            client_id=str(token_details["client_id"]),
            role=str(token_details["role"]),
            scopes=[str(scope) for scope in token_details["scopes"]],
        )
        return await call_next(request)

    def _is_public(self, path: str) -> bool:
        public_paths = {
            "/",
            "/health",
            "/openapi.json",
            self.settings.docs_path,
            f"{self.settings.docs_path}/oauth2-redirect",
            "/auth/demo-token",
        }
        if path in public_paths:
            return True
        return not any(path.startswith(prefix) for prefix in self.protected_prefixes)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)
        logger.info("%s %s -> %s", request.method, request.url.path, response.status_code)
        return response


def get_principal(request: Request) -> DemoPrincipal:
    principal = getattr(request.state, "principal", None)
    if principal is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return principal


def require_scope(request: Request, scope: str) -> DemoPrincipal:
    principal = get_principal(request)
    if not principal.has_scope(scope):
        raise HTTPException(
            status_code=403,
            detail=f"Scope '{scope}' is required for this operation",
        )
    return principal
