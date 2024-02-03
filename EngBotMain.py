import asyncio
from aiogram import Bot, Dispatcher
from handlers import EngBotCommands, EngBotV, EngBotQ


async def main():
    # session = AiohttpSession(proxy="http://proxy.server:3128")
    TOKEN = '6876575217:AAFYajfnd13mz_Rkp8vv1Ks6OXsOR4_g-xE'
    bot = Bot(TOKEN, parse_mode="HTML")
    dp = Dispatcher(bot=bot)

    dp.include_routers(EngBotCommands.router, EngBotV.router, EngBotQ.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())