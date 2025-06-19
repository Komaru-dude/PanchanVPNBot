import os
import logging
import asyncio

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from bot.handlers.start import start_router
from bot.handlers.stats import stats_router
from bot.handlers.request import req_router
from bot.utils.api import Api

logging.basicConfig(level=logging.INFO)
load_dotenv()

token = str(os.getenv("BOT_API_TOKEN"))
bot = Bot(token)
dp = Dispatcher()

async def init_profiles(api: Api):
    if not await api.check_user_template_exists("vless_free"):
        logging.info("Бесплатный профиль не существует, создаём")
        await api.add_user_template(name="vless_free", data_limit="2147483648", inbounds={"vless": ["VLESS TCP REALITY"]})
    else:
        logging.info("Бесплатный профиль существует")
    if not await api.check_user_template_exists("vless_30"):
        logging.info("Платный 30 дневный профиль не существует, создаём")
        await api.add_user_template(name="vless_30", expire_duration=2592000, inbounds={"vless": ["VLESS TCP REALITY"]})
    else:
        logging.info("Платный 30 дневный профиль существует")

async def main():
    api = Api()
    await api.init()
    await init_profiles(api)
    dp["api"] = api
    dp.include_routers(start_router, stats_router, req_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())