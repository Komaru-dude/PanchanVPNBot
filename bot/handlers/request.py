import os
from datetime import datetime, timedelta
from aiohttp.web import HTTPUnauthorized

from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

from bot.filters.chat_type import ChatTypeFilter
from bot.utils.api import Api

req_router = Router()
ADMINS = os.getenv('ADMIN_IDS')
admins = list(map(int, ADMINS.split(',')))
pending_requests = {} # FIXME: Позже заменить на asyncpg или другую бд, данная реализация не имеет устойчивости к рестартам
allowed_plans = ("vless_free", "vless_30", "vless_14", "vless_7") # FIXME: Опять же, лучше сделать без хардкодинга

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

    if not plan in allowed_plans:
        await message.reply(f"Такого плана не существует, вот существующие: {allowed_plans}")
        return

    pending_requests[user_id] = plan

    text = f"Пользователь @{message.from_user.username or message.from_user.full_name} " \
           f"({user_id}) запросил подтверждение для плана: {plan}"

    for admin_id in admins:
        try:
            await bot.send_message(admin_id, text, reply_markup=make_confirm_kb(user_id, plan))
        except Exception as e:
            print(f"Не удалось отправить администратору {admin_id}: {e}")

    await message.answer("Запрос отправлен администраторам на подтверждение.")

@req_router.callback_query(F.data.startswith("confirm"))
async def process_confirmation(callback: CallbackQuery, bot: Bot, api: Api):
    if callback.from_user.id not in admins:
        await callback.answer("Ты не админ и не можешь это делать.", show_alert=True)
        return

    _, user_id_str, plan, action = callback.data.split(":")
    user_id = int(user_id_str)

    if user_id not in pending_requests:
        await callback.answer("Этот запрос уже обработан или не существует.", show_alert=True)
        return

    if action == "yes":
        answer_text = f"✅ Ваш запрос на план '{plan}' подтверждён!\n⏰ Ожидайте ссылки"
        await callback.message.edit_text(callback.message.text + "\n\n✅ Подтверждено")
        try:
            await bot.send_message(user_id, answer_text)
        except Exception as e:
            print(f"Не удалось уведомить пользователя {user_id}: {e}")

        expire_timestamp = 0
        data_limit_bytes = 0

        plan_duration_part = plan.split('_')[-1] 

        if plan_duration_part.isdigit():
            days = int(plan_duration_part)
            expire_datetime = datetime.now() + timedelta(days=days)
            expire_timestamp = int(expire_datetime.timestamp())
            data_limit_bytes = 0
        elif plan_duration_part == "free":
            expire_timestamp = 0 
            data_limit_bytes = 2 * 1024 * 1024 * 1024  # 2 Гб
        
        try:
            base_username = str(user_id)
            current_username = base_username
            suffix = 0

            while True:
                try:
                    data = await api.add_user(
                        username=current_username,
                        status="active",
                        expire=expire_timestamp,
                        data_limit=data_limit_bytes,
                        data_limit_reset_strategy="no_reset",
                        note="Telegram покупатель"
                    )
                    break
                except HTTPUnauthorized:
                    suffix += 1
                    current_username = f"{base_username}_{suffix}"
                    print(f"Конфликт, пробуем с username = {current_username}")

            del pending_requests[user_id]
            await bot.send_message(
                user_id,
                f"😊 Ваша ссылка готова, гайд по установке смотрите в /install\n\n<code>{data['subscription_url']}</code>",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            print(f"Ошибка при добавлении пользователя через API для {user_id}: {e}")
            await callback.answer("Произошла ошибка при добавлении пользователя через API.", show_alert=True)

    elif action == "no":
        await callback.message.edit_text(callback.message.text + "\n\n❌ Отклонено")
        try:
            await bot.send_message(user_id, "❌ Ваш запрос был отклонен.")
        except Exception as e:
            print(f"Не удалось уведомить пользователя {user_id}: {e}")
        del pending_requests[user_id]

    await callback.answer()
