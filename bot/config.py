"""Конфигурация приложения. Все настройки читаются из переменных окружения."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Telegram
    bot_token: str

    # Внешний API (единственный источник данных, БД нет)
    api_base_url: str = "https://api.example.com"
    api_timeout: float = 10.0

    # JWT
    jwt_secret: str = "super-secret-key"
    jwt_algorithm: str = "HS256"

    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
