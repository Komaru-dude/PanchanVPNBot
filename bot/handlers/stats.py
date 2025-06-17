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

    mem_used_bytes = data["mem_used"]
    mem_total_bytes = data["mem_total"]

    mem_used_mb = f"{(mem_used_bytes / (1024 * 1024)):.2f}" if mem_used_bytes is not None else "N/A"
    mem_total_mb = f"{(mem_total_bytes / (1024 * 1024)):.2f}" if mem_total_bytes is not None else "N/A"

    answer = (
        f"🧠 **Система**\n"
        f"🔖 Версия: `{data['version']}`\n"
        f"💾 ОЗУ: `{mem_used_mb} МБ / {mem_total_mb} МБ`\n"
        f"🧮 CPU: {data['cpu_cores']} ядер, нагрузка: `{data['cpu_usage']}%`\n\n"

        f"👥 **Пользователи**\n"
        f"🔢 Всего: `{data['total_user']}`\n"
        f"🟢 Онлайн: `{data['online_users']}`\n"
        f"⚡️ Активны: `{data['users_active']}`\n"
        f"⏸️ Ожидают: `{data['users_on_hold']}`\n"
        f"⛔️ Отключены: `{data['users_disabled']}`\n"
        f"⌛️ Истёк срок: `{data['users_expired']}`\n"
        f"📉 Ограничены: `{data['users_limited']}`\n\n"

        f"🌐 **Трафик**\n"
        f"⬇️ Входящий: `{data['incoming_bandwidth']} байт`\n"
        f"⬆️ Исходящий: `{data['outgoing_bandwidth']} байт`\n"
        f"🚀 Скорость входящая: `{data['incoming_bandwidth_speed']} Б/с`\n"
        f"🚀 Скорость исходящая: `{data['outgoing_bandwidth_speed']} Б/с`"
    )

    await message.reply(answer, parse_mode=ParseMode.MARKDOWN_V2)