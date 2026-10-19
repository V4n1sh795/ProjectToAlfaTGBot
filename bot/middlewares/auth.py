"""Middleware авторизации по JWT.

Хранение сессий — в памяти процесса (MemoryStorage), без БД.
Неавторизованных пользователей пропускаем только к публичным командам
(/start, /help); остальные хендлеры требуют валидный токен в state.
Срок жизни токена проверяется по полю exp при каждом обновлении state.
"""
from __future__ import annotations

import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject


class AuthMiddleware(BaseMiddleware):
    PUBLIC_COMMANDS = {"/start", "/help"}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        state = data.get("state")
        session: dict[str, Any] = await state.get_data() if state else {}
        expires_at = session.get("expires_at", 0)
        is_expired = expires_at and time.time() > expires_at

        first_word = (event.text or "").split(maxsplit=1)[0].split("@")[0] if event.text else ""
        is_public = first_word in self.PUBLIC_COMMANDS

        if (not session.get("token") or is_expired) and not is_public:
            if is_expired:
                await state.clear()
                await event.answer("⏰ Сессия истекла. Авторизуйтесь заново: /start <токен>")
            else:
                await event.answer(
                    "⛔️ Вы не авторизованы.\n"
                    "Отправьте токен командой: /start <ваш JWT-токен>"
                )
            return None

        # Пробрасываем токен и payload в kwargs хендлера
        data["token"] = session.get("token")
        data["user"] = session.get("user")

        return await handler(event, data)
