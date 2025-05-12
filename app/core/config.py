from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    # Env‑configurable variables
    nyt_api_key: str = Field(..., env="NYT_API_KEY")
    nyt_base_url: str = (
        "https://api.nytimes.com/svc"
    )  # rarely changes, keep constant here
    top_sections: List[str] = [
        "arts",
        "food",
        "movies",
        "travel",
        "science",
    ]
    timeout_seconds: float = 10.0

    @validator("nyt_api_key")
    def _no_placeholder(cls, v: str) -> str:
        if v.strip().lower() in {"changeme", "your_key_here", ""}:
            raise ValueError("A real NYT_API_KEY must be provided.")
        return v

    class Config:  # pydantic settings config
        env_file = ".env"
        env_file_encoding = "utf‑8"


@lru_cache
def get_settings() -> Settings:
    """FastAPI will call this via Depends only once (cached)."""
    return Settings()
