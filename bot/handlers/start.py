from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

start_router = Router()

@start_router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Добро пожаловать В Panchan VPN, здесь вы можете получить ключ для VPN. Чтобы приобрести ключ нужно написать @Panchan3 или @ToboKun. /request чтобы получить ключ")