from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- OpenAI ---
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536

    # --- Database (PostgreSQL + pgvector) ---
    # Example: postgresql+psycopg://user:password@localhost:5432/smartflash
    database_url: str = ""

    # --- Retrieval ---
    default_top_k: int = 5

    def require_openai(self) -> None:
        if not self.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

    def require_database(self) -> None:
        if not self.database_url:
            raise RuntimeError("DATABASE_URL is not configured.")


@lru_cache
def get_settings() -> Settings:
    return Settings()
