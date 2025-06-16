from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

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
        f"🕹 Версия: {data["version"]}\n\n"
        f"🗂 ОЗУ: {mem_used_mb} МБ/{mem_total_mb} МБ\n\n"
        "📈 CPU:\n"
        f"CPU cores: {data["cpu_cores"]}\n"
        f"CPU usage: {data["cpu_usage"]}\n\n"
        f"🟢 Online users: {data["online_users"]}"
    )

    await message.reply(answer)