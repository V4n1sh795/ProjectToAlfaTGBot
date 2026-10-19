"""Клиент внешнего API. Единственный источник данных для бота (БД нет)."""
from __future__ import annotations

from typing import Any

import aiohttp

from bot.config import get_settings


class ApiError(Exception):
    """Ошибка при обращении к внешнему API."""


class ApiClient:
    """Тонкая обёртка над aiohttp. Передаёт JWT пользователя в заголовке
    Authorization: Bearer <token>, API отвечает всеми данными."""

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        self._session = session

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            s = get_settings()
            self._session = aiohttp.ClientSession(
                base_url=s.api_base_url,
                timeout=aiohttp.ClientTimeout(total=s.api_timeout),
            )
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def request(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        json: Any = None,
        params: dict | None = None,
    ) -> Any:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        session = await self._get_session()
        async with session.request(method, path, json=json, params=params, headers=headers) as resp:
            if resp.status == 401:
                raise ApiError("Unauthorized: токен не принят API.")
            if resp.status >= 400:
                text = await resp.text()
                raise ApiError(f"API error {resp.status}: {text}")
            return await resp.json()

    # --- Примеры методов под ваш API ---

    async def get_profile(self, token: str) -> dict:
        return await self.request("GET", "/profile", token=token)

    async def get_items(self, token: str) -> list[dict]:
        return await self.request("GET", "/items", token=token)


# Глобальный синглтон клиента (живёт всё время работы процесса)
api_client = ApiClient()
