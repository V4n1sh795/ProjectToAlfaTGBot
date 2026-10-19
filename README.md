# Telegram Bot (aiogram 3.x, без БД, JWT-авторизация)

Каркас Telegram-бота:
- **Без базы данных** — вся информация приходит из внешнего API (`API_BASE_URL`).
- **Авторизация через JWT** — пользователь присылает токен: `/start <токен>`,
  бот проверяет подпись/срок действия и дополнительно валидирует токен на API.
- Сессии хранятся в памяти процесса (`MemoryStorage`) — перезапуск бота
  требует повторной авторизации пользователей.
- Запуск через **docker compose**, long-polling (webhook опционально).

## Структура

```
bot/
├── __main__.py            # точка входа (polling)
├── config.py              # настройки из ENV (pydantic-settings)
├── handlers/
│   ├── auth.py            # /start <jwt>, /login, /logout
│   ├── common.py          # /help, /ping
│   └── api.py             # /profile, /items — данные с внешнего API
├── middlewares/
│   └── auth.py            # AuthMiddleware: пускает только авторизованных
└── services/
    ├── auth.py            # декодирование/проверка JWT (PyJWT)
    └── api.py             # aiohttp-клиент внешнего API (Bearer <token>)
```

## Быстрый старт

```bash
cp .env.example .env       # заполнить BOT_TOKEN, API_BASE_URL, JWT_SECRET
docker compose up -d --build
docker compose logs -f bot
```

Локально без Docker:

```bash
pip install -r requirements.txt
python -m bot
```

## Как работает авторизация

1. Внешний сервис выдаёт пользователю JWT (например, после логина на сайте).
2. Пользователь отправляет боту `/start <токен>`.
3. `bot/services/auth.py` проверяет подпись (`JWT_SECRET`, алгоритм `HS256`)
   и срок действия `exp`; `bot/services/api.py` дополнительно дёргает
   `GET /profile` с `Authorization: Bearer <token>` — источник истины API.
4. `AuthMiddleware` блокирует все команды, кроме `/start` и `/help`,
   пока в state нет валидного токена; истёкшую сессию сбрасывает.

## Доработка под свой проект

- Добавьте методы в `ApiClient` под эндпоинты вашего API.
- Новые команды — в `bot/handlers/`, зарегистрируйте роутер в `__main__.py`.
- Для webhook: разкомментируйте `ports` в `docker-compose.yml` и замените
  `start_polling` на `Bot(webhook=...)` + aiohttp-сервер.

⚠️ Если бот будет масштабироваться (несколько реплик), MemoryStorage
замените на Redis — но для одного контейнера её достаточно.
