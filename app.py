import asyncio
import logging
import os
import sys
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import BOT_TOKEN
import database as db
import handlers_user
import handlers_admin

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

WEBHOOK_PATH = "/webhook"

# Фоновый пингер самого себя каждые 10 минут, чтобы Render никогда не уходил в спящий режим
async def self_pinger():
    base_url = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
    if not base_url:
        logger.info("RENDER_EXTERNAL_URL не задан, self-pinger отключён.")
        return
    logger.info(f"Self-pinger запущен для адреса: {base_url}")
    await asyncio.sleep(60)
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(f"{base_url}/health", timeout=15) as resp:
                    logger.info(f"Self-ping отправлен, статус: {resp.status}")
            except Exception as e:
                logger.warning(f"Ошибка self-ping: {e}")
            await asyncio.sleep(600)  # каждые 10 минут

async def on_startup(bot: Bot):
    await db.init_db()
    logger.info("База данных инициализирована.")

    # Регистрация видимых команд в Telegram
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

    # Запуск авто-пингера
    asyncio.create_task(self_pinger())

    # Настройка Webhook через Render URL
    base_url = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
    if base_url:
        webhook_url = f"{base_url}{WEBHOOK_PATH}"
        logger.info(f"Устанавливаем Webhook на: {webhook_url}")
        await bot.set_webhook(
            url=webhook_url,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=False
        )
        logger.info("Webhook успешно активирован в Telegram!")
    else:
        logger.warning("RENDER_EXTERNAL_URL отсутствует, запускается fallback режим.")

async def on_shutdown(bot: Bot):
    logger.info("Остановка бота...")
    await bot.session.close()

async def handle_health(request):
    return web.Response(text="Bot «Без осуждения» is running 24/7!", content_type="text/plain")

def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не задан!")
        return

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(handlers_admin.router)
    dp.include_router(handlers_user.router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)

    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    webhook_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    port = int(os.environ.get("PORT", 7860))
    logger.info(f"Запуск веб-сервера на порту {port}...")
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
