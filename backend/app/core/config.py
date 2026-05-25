from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PLACEHOLDER_GEMINI_KEY = "your_gemini_api_key"
PLACEHOLDER_TAVILY_KEY = "your_tavily_api_key"


class Settings(BaseSettings):
    """Runtime configuration populated from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Fact-Check Agent API"
    environment: str = "development"
    gemini_api_key: str | None = None
    tavily_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    frontend_origins: str = "http://localhost:5173"
    max_upload_mb: int = Field(default=10, ge=1, le=50)
    max_claims: int = Field(default=18, ge=1, le=50)
    max_document_chars: int = Field(default=100_000, ge=5_000, le=500_000)
    max_search_results: int = Field(default=5, ge=1, le=10)
    verification_concurrency: int = Field(default=4, ge=1, le=10)
    ai_timeout_seconds: float = Field(default=90.0, ge=10.0, le=300.0)

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]

    @property
    def maximum_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def gemini_is_configured(self) -> bool:
        return bool(
            self.gemini_api_key
            and self.gemini_api_key.strip()
            and self.gemini_api_key.strip() != PLACEHOLDER_GEMINI_KEY
            and not self.gemini_model.strip().startswith("AIza")
        )

    @property
    def tavily_is_configured(self) -> bool:
        return bool(
            self.tavily_api_key
            and self.tavily_api_key.strip()
            and self.tavily_api_key.strip() != PLACEHOLDER_TAVILY_KEY
        )

    @property
    def configuration_issues(self) -> list[str]:
        issues: list[str] = []
        if not self.gemini_api_key or self.gemini_api_key.strip() == PLACEHOLDER_GEMINI_KEY:
            issues.append("Set a real GEMINI_API_KEY in backend/.env.")
        if self.gemini_model.strip().startswith("AIza"):
            issues.append(
                "GEMINI_MODEL looks like an API key. Set it to a model name such as "
                "gemini-2.5-flash and put the API key in GEMINI_API_KEY."
            )
        if not self.tavily_api_key or self.tavily_api_key.strip() == PLACEHOLDER_TAVILY_KEY:
            issues.append("Set a real TAVILY_API_KEY in backend/.env.")
        return issues


@lru_cache
def get_settings() -> Settings:
    return Settings()
