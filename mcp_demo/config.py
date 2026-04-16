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
    demo_bearer_token: str = "course-demo-token"
    auth_header_name: str = "Authorization"
    enable_request_logging: bool = True

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


@lru_cache(maxsize=1)
def get_settings() -> DemoSettings:
    return DemoSettings()
