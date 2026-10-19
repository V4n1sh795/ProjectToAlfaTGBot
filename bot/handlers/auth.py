"""Команды авторизации: /start <jwt>, размлогин."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.services.api import ApiError, api_client
from bot.services.auth import AuthError, decode_token

router = Router(name="auth")


@router.message(CommandStart(deep_link=True))
async def cmd_start_with_token(message: Message, state: FSMContext) -> None:
    """/start <JWT-токен> — проверяем подпись и срок действия, кладём в state."""
    token = message.text.split(maxsplit=1)[1].strip()
    try:
        payload = decode_token(token)
    except AuthError as e:
        await message.answer(f"❌ {e}")
        return

    # Дополнительная проверка токена на стороне API (источник истины — API)
    try:
        profile = await api_client.get_profile(token)
    except ApiError as e:
        await message.answer(f"⚠️ Не удалось проверить токен через API: {e}")
        return

    await state.update_data(
        token=token,
        expires_at=payload.expires_at,
        user={"id": payload.user_id, "username": payload.username},
    )
    name = profile.get("name") or payload.username or message.from_user.full_name
    await message.answer(f"✅ Авторизован: {name}\n\nДоступные команды:\n/help")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "👋 Привет!\n"
        "Для авторизации отправьте: /start <ваш JWT-токен>\n"
        "Токен можно получить в личном кабинете."
    )


@router.message(Command("login"))
async def cmd_login(message: Message) -> None:
    """Просто показать инструкцию, если пользователь уже внутри."""
    await message.answer("Чтобы сменить аккаунт: /start <новый токен>")


@router.message(Command("logout"))
async def cmd_logout(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("👋 Сессия завершена. Новый вход: /start <токен>")
