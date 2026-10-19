"""Точка входа: python -m bot"""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import get_settings
from bot.handlers import api, auth, common
from bot.middlewares.auth import AuthMiddleware
from bot.services.api import api_client


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    # MemoryStorage — без БД. Сессии живут только в памяти процесса.
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(AuthMiddleware())

    # Порядок важен: auth-команды раньше защищённых роутеров
    dp.include_router(auth.router)
    dp.include_router(common.router)
    dp.include_router(api.router)

    try:
        me = await bot.get_me()
        logging.info("Бот @%s запущен (long polling)", me.username)
        await dp.start_polling(bot)
    finally:
        await api_client.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
