import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from handlers import EngBotCommands, EngBotV, EngBotQ, EngBotWords, EngBotTheory
from utils import init_session, close_session, parse_dict
from aiogram.client.bot import DefaultBotProperties
from dotenv import load_dotenv
from utils import storage
from data.EngBotDB import main as create_db

async def main():
    load_dotenv()

    # session = AiohttpSession(proxy="http://proxy.server:3128")
    PORT = int(os.getenv("PORT", 10000))
    bot = Bot(os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=storage)
    dp.include_routers(
        EngBotCommands.router,
        EngBotV.router,
        EngBotQ.router,
        EngBotWords.router,
        EngBotTheory.router,
    )
    logging.basicConfig(level=logging.INFO)
    logging.info("Bot is enabled")

    await create_db()

    await init_session()
    # Warm up connection
    await parse_dict("bot")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, host='0.0.0.0', port=PORT)

    await close_session()


if __name__ == "__main__":
    asyncio.run(main())
