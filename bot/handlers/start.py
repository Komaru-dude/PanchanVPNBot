from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

start_router = Router()

@start_router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("👋 Добро пожаловать в <b>Panchan VPN</b>!\n\nВ этом боте вы можете получить ключ для VPN.\n\nЧтобы приобрести ключ, напишите @Panchan3 или @ToboKun.\n\nИспользуйте команду /request, чтобы получить ключ.", parse_mode=ParseMode.HTML)