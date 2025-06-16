from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.filters.admin_command import AdminCmdFilter
from bot.filters.chat_type import ChatTypeFilter

stats_router = Router()

