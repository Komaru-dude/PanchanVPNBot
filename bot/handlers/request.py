import os

from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.filters.chat_type import ChatTypeFilter
from bot.utils.api import Api

req_router = Router()
ADMINS = os.getenv('ADMIN_IDS')
admins = list(map(int, ADMINS.split(',')))
pending_requests = {} # FIXME: Позже заменить на asyncpg или другую бд, данная реализация не имеет устойчивости к рестартам

def make_confirm_kb(user_id: int, plan: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтвердить",
                callback_data=f"confirm:{user_id}:{plan}:yes"
            ),
            InlineKeyboardButton(
                text="❌ Отклонить",
                callback_data=f"confirm:{user_id}:{plan}:no"
            ),
        ]
    ])

@req_router.message(Command("request"), ChatTypeFilter("private"))
async def cmd_request(message: Message, bot: Bot):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Пожалуйста, укажи план после команды, например: /request vless_free")
        return
    plan = args[1].strip()
    user_id = message.from_user.id

    pending_requests[user_id] = plan

    text = f"Пользователь @{message.from_user.username or message.from_user.full_name} " \
           f"({user_id}) запросил подтверждение для плана: {plan}"

    for admin_id in admins:
        try:
            await bot.send_message(admin_id, text, reply_markup=make_confirm_kb(user_id, plan))
        except Exception as e:
            print(f"Не удалось отправить администратору {admin_id}: {e}")

    await message.answer("Запрос отправлен администраторам на подтверждение.")

@req_router.callback_query(F.data.startwith() == "confirm")
async def process_confirmation(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id not in admins:
        await callback.answer("Ты не админ и не можешь это делать.", show_alert=True)
        return

    _, user_id_str, plan, action = callback.data.split(":")
    user_id = int(user_id_str)

    if user_id not in pending_requests:
        await callback.answer("Этот запрос уже обработан или не существует.", show_alert=True)
        return

    if action == "yes":
        answer_text = f"✅ Ваш запрос на план '{plan}' подтверждён!"
        await callback.message.edit_text(callback.message.text + "\n\n✅ Подтверждено")
    else:
        answer_text = f"❌ Ваш запрос на план '{plan}' отклонён."
        await callback.message.edit_text(callback.message.text + "\n\n❌ Отклонено")

    try:
        await bot.send_message(user_id, answer_text)
    except Exception as e:
        print(f"Не удалось уведомить пользователя {user_id}: {e}")

    del pending_requests[user_id]

    await callback.answer()
