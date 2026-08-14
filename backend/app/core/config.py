from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")

    service_name: str = "supply-chain-ops-api"
    version: str = "0.1.0"
    environment: str = "local"


@lru_cache
def get_settings() -> Settings:
    return Settings()
