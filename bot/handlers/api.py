"""Примеры хендлеров, которые берут все данные из внешнего API (БД нет).
Токен пользователя приходит из AuthMiddleware через kwargs `token`.
"""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.services.api import ApiError, api_client

router = Router(name="api")


@router.message(Command("profile"))
async def cmd_profile(message: Message, token: str | None) -> None:
    try:
        profile = await api_client.get_profile(token)
    except ApiError as e:
        await message.answer(f"⚠️ {e}")
        return

    await message.answer(
        f"👤 Профиль:\n"
        f"Имя: {profile.get('name', '—')}\n"
        f"Email: {profile.get('email', '—')}"
    )


@router.message(Command("items"))
async def cmd_items(message: Message, token: str | None) -> None:
    try:
        items = await api_client.get_items(token)
    except ApiError as e:
        await message.answer(f"⚠️ {e}")
        return

    if not items:
        await message.answer("Список пуст.")
        return

    lines = [f"• {it.get('title', it)}" for it in items[:20]]
    await message.answer("📋 Элементы:\n" + "\n".join(lines))
