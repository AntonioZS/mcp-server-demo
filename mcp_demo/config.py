from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DemoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "MCP Server Demo"
    environment: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    mcp_path: str = "/mcp"
    docs_path: str = "/docs"
    log_level: str = "INFO"
    allowed_origins: list[str] = Field(default_factory=lambda: ["*"])
    demo_presenter_token: str = "course-demo-token"
    demo_viewer_token: str = "course-viewer-token"
    auth_header_name: str = "Authorization"
    enable_request_logging: bool = True

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def demo_token_catalog(self) -> dict[str, dict[str, str | list[str]]]:
        return {
            self.demo_presenter_token: {
                "role": "presenter",
                "client_id": "course-presenter",
                "scopes": ["mcp:read", "mcp:execute", "demo:admin"],
            },
            self.demo_viewer_token: {
                "role": "viewer",
                "client_id": "course-viewer",
                "scopes": ["mcp:read"],
            },
        }


@lru_cache(maxsize=1)
def get_settings() -> DemoSettings:
    return DemoSettings()
