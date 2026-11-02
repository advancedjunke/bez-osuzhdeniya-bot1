import asyncio
import logging
import sys
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

async def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не задан! Укажите токен в файле .env или переменных окружения.")
        return

    await db.init_db()
    logger.info("База данных инициализирована.")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.include_router(handlers_admin.router)
    dp.include_router(handlers_user.router)

    # Настройка видимых команд в меню Telegram
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

    logger.info("Бот запущен и готов к работе...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
