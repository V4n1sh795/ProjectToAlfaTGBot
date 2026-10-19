"""Работа с JWT-токенами: проверка подписи и извлечение полезной нагрузки.

Схема авторизации: пользователь получает JWT от внешнего API (например, после
веб-авторизации) и присылает его боту (/start <token>) либо отправляет в личке.
Бот валидирует токен и сохраняет payload в memory-state (без БД).
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import jwt  # PyJWT

from bot.config import get_settings


class AuthError(Exception):
    """Ошибка авторизации: токен недействителен/истёк."""


@dataclass(frozen=True)
class TokenPayload:
    user_id: int          # telegram user id внутри токена
    username: str | None
    expires_at: int       # unix timestamp

    @property
    def expired(self) -> bool:
        return time.time() > self.expires_at


def create_token(user_id: int, username: str | None = None, ttl: int = 3600) -> str:
    """Генерация токена (нужно для тестов; в проде токены выдаёт внешний API)."""
    s = get_settings()
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "tg_user_id": user_id,
        "username": username,
        "iat": now,
        "exp": now + ttl,
    }
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algorithm)


def decode_token(token: str) -> TokenPayload:
    """Проверка подписи и срока действия. Бросает AuthError при проблемах."""
    s = get_settings()
    try:
        payload = jwt.decode(
            token,
            s.jwt_secret,
            algorithms=[s.jwt_algorithm],
            options={"require": ["exp", "sub"]},
        )
    except jwt.ExpiredSignatureError as e:
        raise AuthError("Токен истёк, авторизуйтесь заново.") from e
    except jwt.InvalidTokenError as e:
        raise AuthError("Недействительный токен.") from e

    return TokenPayload(
        user_id=int(payload.get("tg_user_id", payload["sub"])),
        username=payload.get("username"),
        expires_at=int(payload["exp"]),
    )
