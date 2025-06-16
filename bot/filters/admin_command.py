import os
from aiogram.filters import BaseFilter
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

admin_ids = set(map(int, os.getenv("ADMIN_IDS", "").split(",")))

class AdminCmdFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user is None:
            return False
        user_id = message.from_user.id
        return user_id in admin_ids
