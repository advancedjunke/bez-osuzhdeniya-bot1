import asyncio
import logging
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, BotCommandScopeDefault

from config import BOT_TOKEN
import database as db
import handlers_user
import handlers_admin

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Web-сервер для проверки статуса Hugging Face Spaces (порт 7860)
async def handle_health(request):
    return web.Response(text="Bot «Без осуждения» is running 24/7!", content_type="text/plain")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 7860))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Web healthcheck server started on port {port}")

async def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не задан!")
        return

    await db.init_db()
    logger.info("База данных инициализирована.")

    # Запуск легковесного веб-сервера для Hugging Face
    await start_web_server()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.include_router(handlers_admin.router)
    dp.include_router(handlers_user.router)

    commands = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="anketa", description="Отправить свою проблему"),
        BotCommand(command="about", description="Кто я такой?"),
        BotCommand(command="platno", description="Гарантированный разбор и подписка"),
        BotCommand(command="status", description="Статус подписки"),
        BotCommand(command="pravila", description="Правила проекта"),
        BotCommand(command="help", description="Помощь")
    ]
    try:
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    except Exception as e:
        logger.warning(f"Не удалось установить команды: {e}")

    logger.info("Бот запущен и работает круглосуточно...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
