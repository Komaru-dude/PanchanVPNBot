import os
import logging
import asyncio

from aiogram import Bot, Dispatcher

from bot.handlers.start import start_router

logging.basicConfig(level=logging.INFO)

token = str(os.getenv("BOT_API_TOKEN"))
bot = Bot(token)
dp = Dispatcher()

async def main():
    dp.include_router(start_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())