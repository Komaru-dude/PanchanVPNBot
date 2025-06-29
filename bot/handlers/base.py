from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

base_router = Router()

@base_router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("👋 Добро пожаловать в <b>Panchan VPN</b>!\n\nВ этом боте вы можете получить ключ для VPN.\n\nЧтобы приобрести ключ, напишите @Panchan3 или @ToboKun.\n\nИспользуйте команду /request, чтобы получить ключ.", parse_mode=ParseMode.HTML)

@base_router.message(Command("install"))
async def send_install_instructions(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📱 Android (v2RayTun)", url="https://play.google.com/store/apps/details?id=com.v2raytun.android"),
        InlineKeyboardButton(text="🍏 iOS (v2RayTun)", url="https://apps.apple.com/en/app/v2raytun/id6476628951"),
        InlineKeyboardButton(text="💻 Windows (v2RayTun)", url="https://storage.v2raytun.com/v2RayTun_Setup.exe"),
    )
    await message.reply(
        f"**Установка VLESS VPN через v2RayTun на всех платформах:**\n\n"
        f"1. Установите v2RayTun на ваше устройство, выбрав кнопку ниже.\n"
        f"2. Скопируйте вашу уникальную ссылку подписки(которую получили из одобренного реквеста):\n\n"
        f"3. Откройте v2RayTun, нажмите `+`, выберите `Импорт из буфера обмена`.\n"
        f"4. Нажмите подключиться.\n"
        f"5. Наслаждайтесь",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )