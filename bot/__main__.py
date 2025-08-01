import os
import logging
import asyncio

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from bot.handlers.base import base_router
from bot.handlers.stats import stats_router
from bot.handlers.request import req_router
from bot.middlewares.only_private import OnlyPrivate
from bot.utils.api import Api

logging.basicConfig(level=logging.INFO)
load_dotenv()

token = str(os.getenv("BOT_API_TOKEN"))
bot = Bot(token)
dp = Dispatcher()

async def main():
    api = Api()
    await api.init()
    dp["api"] = api
    dp.callback_query.outer_middleware(OnlyPrivate())
    dp.include_routers(base_router, stats_router, req_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())