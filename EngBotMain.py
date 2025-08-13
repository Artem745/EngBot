import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiohttp import web
from handlers import EngBotCommands, EngBotV, EngBotQ, EngBotWords, EngBotTheory
from utils import init_session, close_session, parse_dict
from aiogram.client.bot import DefaultBotProperties
from dotenv import load_dotenv
from utils import storage
from data.EngBotDB import main as create_db, DB_save_data

async def web_server():
    async def handle(request):
        return web.Response(text="Bot is running")

    app = web.Application()
    app.router.add_get("/", handle)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
    await site.start()


async def main():
    load_dotenv()

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

    # async def save_data():
    #     load_dotenv()
    #     admin_id = os.getenv("ADMIN_ID")
    #     if admin_id:
    #         data = await DB_save_data(admin_id)
    #         await bot.send_message(chat_id=admin_id, text=str(data))

    # dp.shutdown.register(save_data)

    await create_db()
    await init_session()
    await parse_dict("bot")
    await bot.delete_webhook(drop_pending_updates=True)

    await asyncio.gather(
        web_server(),
        dp.start_polling(bot),
    )

    await close_session()

if __name__ == "__main__":
    asyncio.run(main())
