from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mcp_demo.auth import BearerTokenMiddleware, RequestLoggingMiddleware
from mcp_demo.config import get_settings
from mcp_demo.mcp_server import create_mcp_server

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

mcp = create_mcp_server()
mcp_http_app = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with mcp.session_manager.run():
        yield


app = FastAPI(title=settings.app_name, docs_url=settings.docs_path, lifespan=lifespan)

if settings.allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if settings.enable_request_logging:
    app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(BearerTokenMiddleware, settings=settings, protected_prefixes=(settings.mcp_path, "/demo"))
app.mount(settings.mcp_path, mcp_http_app)


@app.get("/")
def root() -> dict[str, object]:
    return {
        "name": settings.app_name,
        "transport": "streamable-http",
        "mcp_endpoint": f"{settings.mcp_path}/",
        "docs": settings.docs_path,
        "secured_paths": [settings.mcp_path, "/demo"],
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@app.get("/auth/demo-token")
def demo_token() -> dict[str, str]:
    return {
        "token_type": "Bearer",
        "access_token": settings.demo_bearer_token,
        "usage": f"Authorization: Bearer {settings.demo_bearer_token}",
    }


@app.get("/demo/overview")
def demo_overview() -> dict[str, object]:
    return {
        "tools": ["estimate_delivery_effort", "summarize_release_notes", "process_project_files"],
        "resources": ["course://outline", "project://demo/status"],
        "prompts": ["explain_mcp_flow", "architecture_review_prompt"],
    }
