"""Публичные команды: /help, /ping."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="common")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "🤖 Бот-обёртка над внешним API\n\n"
        "Команды:\n"
        "/start <токен> — авторизация по JWT\n"
        "/profile — профиль (данные с API)\n"
        "/items — список (данные с API)\n"
        "/logout — завершить сессию\n"
        "/help — эта справка"
    )


@router.message(Command("ping"))
async def cmd_ping(message: Message) -> None:
    await message.answer("🏓 Понг! Бот на связи.")
