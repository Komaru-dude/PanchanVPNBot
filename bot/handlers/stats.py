from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

from bot.utils.api import Api
from bot.filters.admin_command import AdminCmdFilter
from bot.filters.chat_type import ChatTypeFilter

stats_router = Router()

@stats_router.message(Command("stats"), AdminCmdFilter(), ChatTypeFilter("private"))
async def cmd_stats(message: Message, api: Api):
    data = await api.get_stats()

    # Конвертация ОЗУ в МБ
    mem_used_bytes = data["mem_used"]
    mem_total_bytes = data["mem_total"]
    mem_used_mb = f"{(mem_used_bytes / (1024 * 1024)):.2f}" if mem_used_bytes is not None else "N/A"
    mem_total_mb = f"{(mem_total_bytes / (1024 * 1024)):.2f}" if mem_total_bytes is not None else "N/A"

    # Конвертация трафика из байт в МБ
    incoming_bandwidth_mb = f"{(data['incoming_bandwidth'] / (1024 * 1024)):.2f}" if data['incoming_bandwidth'] is not None else "N/A"
    outgoing_bandwidth_mb = f"{(data['outgoing_bandwidth'] / (1024 * 1024)):.2f}" if data['outgoing_bandwidth'] is not None else "N/A"

    # Конвертация скорости из Б/с в Мбит/с (1 байт = 8 бит)
    # Мбит/с = (Байт/с * 8) / (1000 * 1000)
    incoming_bandwidth_speed_mbps = f"{(data['incoming_bandwidth_speed'] * 8 / (1000 * 1000)):.2f}" if data['incoming_bandwidth_speed'] is not None else "N/A"
    outgoing_bandwidth_speed_mbps = f"{(data['outgoing_bandwidth_speed'] * 8 / (1000 * 1000)):.2f}" if data['outgoing_bandwidth_speed'] is not None else "N/A"


    answer = (
        f"🧠 <b>Система</b>\n"
        f"🔖 Версия: <code>{data['version']}</code>\n"
        f"💾 ОЗУ: <code>{mem_used_mb} МБ / {mem_total_mb} МБ</code>\n"
        f"🧮 CPU: {data['cpu_cores']} ядер, нагрузка: <code>{data['cpu_usage']}%</code>\n\n"

        f"👥 <b>Пользователи</b>\n"
        f"🔢 Всего: <code>{data['total_user']}</code>\n"
        f"🟢 Онлайн: <code>{data['online_users']}</code>\n"
        f"⚡️ Активны: <code>{data['users_active']}</code>\n"
        f"⏸️ Ожидают: <code>{data['users_on_hold']}</code>\n"
        f"⛔️ Отключены: <code>{data['users_disabled']}</code>\n"
        f"⌛️ Истёк срок: <code>{data['users_expired']}</code>\n"
        f"📉 Ограничены: <code>{data['users_limited']}</code>\n\n"

        f"🌐 <b>Трафик</b>\n"
        f"⬇️ Входящий: <code>{incoming_bandwidth_mb} МБ</code>\n"
        f"⬆️ Исходящий: <code>{outgoing_bandwidth_mb} МБ</code>\n"
        f"🚀 Скорость входящая: <code>{incoming_bandwidth_speed_mbps} Мбит/с</code>\n"
        f"🚀 Скорость исходящая: <code>{outgoing_bandwidth_speed_mbps} Мбит/с</code>"
    )

    await message.reply(answer, parse_mode=ParseMode.HTML)