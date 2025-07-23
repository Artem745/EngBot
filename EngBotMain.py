import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from handlers import EngBotCommands, EngBotV, EngBotQ, EngBotWords
from aiogram.client.bot import DefaultBotProperties
from dotenv import load_dotenv


async def main():
    load_dotenv()

    # session = AiohttpSession(proxy="http://proxy.server:3128")
    bot = Bot(os.getenv("TOKEN"), default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(bot=bot)

    dp.include_routers(
        EngBotCommands.router, EngBotV.router, EngBotQ.router, EngBotWords.router
    )

    logging.basicConfig(level=logging.INFO)
    logging.info("Bot is enabled")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
