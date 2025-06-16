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

    answer = (
        f"🕹 Версия: {data["version"]}\n\n"
        f"🗂 ОЗУ: {data["mem_used"]}/{data["mem_total"]}\n\n"
        "📈 CPU:\n"
        f"CPU cores: {data["cpu_cores"]}\n"
        f"CPU usage: {data["cpu_usage"]}\n\n"
        f"🟢 Online users: {data["online_users"]}"
    )

    await message.reply(answer)