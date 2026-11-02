from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS, CHANNEL_ID
import database as db
from materials import MATERIALS

router = Router()

class AdminStates(StatesGroup):
    waiting_for_reply_text = State()
    waiting_for_broadcast = State()

# Фильтр на админа
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    stats = await db.get_stats()
    text = (
        "👑 *Панель управления проектом «Без осуждения»*\n\n"
        f"👥 Всего пользователей: *{stats['users']}*\n"
        f"📝 Всего анкет: *{stats['submissions']}*\n"
        f"💎 Активных платных подписчиков: *{stats['subscribers']}*\n\n"
        "Команды:\n"
        "/subscribers — список активных подписчиков (счётчики 1/3, 2/3)\n"
        "/stats — общая статистика\n"
        "/broadcast — разослать сообщение всем пользователям бота"
    )
    await message.answer(text, parse_mode="Markdown")

@router.message(Command("subscribers"))
async def cmd_subscribers(message: Message):
    if not is_admin(message.from_user.id):
        return
    subs = await db.get_all_subscribers()
    if not subs:
        await message.answer("Активных подписчиков пока нет.")
        return
    
    lines = ["📋 *Активные подписчики (трекер):*\n"]
    for s in subs:
        username = f"@{s['username']}" if s['username'] else s['first_name'] or f"ID {s['user_id']}"
        lines.append(
            f"• {username} | Использовано: *{s['reviews_used']}/{s['reviews_total']}* | До: {s['end_date'][:10]}"
        )
    await message.answer("\n".join(lines), parse_mode="Markdown")

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    stats = await db.get_stats()
    text = (
        f"📊 *Статистика проекта:*\n"
        f"• Пользователей: {stats['users']}\n"
        f"• Анкет: {stats['submissions']}\n"
        f"• Активных подписок: {stats['subscribers']}"
    )
    await message.answer(text, parse_mode="Markdown")

# --- Ответ автору анкеты ---

@router.callback_query(F.data.startswith("adm_reply:"))
async def start_admin_reply(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    parts = callback.data.split(":")
    sub_id, target_user_id = int(parts[1]), int(parts[2])
    
    await state.update_data(reply_sub_id=sub_id, reply_user_id=target_user_id)
    await state.set_state(AdminStates.waiting_for_reply_text)
    
    await callback.message.answer(
        f"✍️ Напиши текст разбора для пользователя `{target_user_id}` (анкета #{sub_id}).\n"
        "Твой ответ будет отправлен ему в личные сообщения от имени бота."
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_reply_text)
async def process_admin_reply_text(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    await state.clear()
    
    target_user_id = data["reply_user_id"]
    sub_id = data["reply_sub_id"]
    
    user_msg = (
        "✨ *Разбор твоей ситуации от автора проекта «Без осуждения»:*\n\n"
        f"{message.text}\n\n"
        "— Проект «Без осуждения»"
    )
    try:
        await bot.send_message(target_user_id, user_msg, parse_mode="Markdown")
        await message.answer(f"✅ Разбор успешно доставлен пользователю (анкета #{sub_id}).")
    except Exception as e:
        await message.answer(f"❌ Ошибка отправки пользователю: {e}")

# --- Отправка готового мини-гайда ---

@router.callback_query(F.data.startswith("adm_guide:"))
async def send_auto_guide(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        return
    parts = callback.data.split(":")
    sub_id, target_user_id = int(parts[1]), int(parts[2])
    
    sub = await db.get_submission(sub_id)
    if not sub:
        await callback.answer("Анкета не найдена.")
        return
    
    tema = sub["tema"]
    guide_text = MATERIALS.get(tema, MATERIALS["Личное, не с кем обсудить"])
    
    try:
        await bot.send_message(
            target_user_id,
            f"Привет! Спасибо за заполнение анкеты. Как и обещали в правилах, направляем тебе материал по твоей теме:\n\n{guide_text}",
            parse_mode="Markdown"
        )
        await callback.message.answer(f"📚 Готовый гайд по теме *«{tema}»* успешно отправлен пользователю `{target_user_id}`.")
    except Exception as e:
        await callback.message.answer(f"❌ Не удалось отправить: {e}")
    await callback.answer()

# --- Публикация в канал (анонимно) ---

@router.callback_query(F.data.startswith("adm_pub:"))
async def publish_anonymous_to_channel(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        return
    sub_id = int(callback.data.split(":")[1])
    sub = await db.get_submission(sub_id)
    if not sub:
        await callback.answer("Анкета не найдена.")
        return
    
    post_text = (
        f"🏷 #{sub['tema'].replace(' ', '_')}\n\n"
        f"🗣 *Анонимная ситуация #{sub_id}*\n\n"
        f"*Факты:*\n{sub['situaciya']}\n\n"
        f"*Что уже пробовалось:*\n{sub['popytki']}\n\n"
        f"*Вопрос:*\n{sub['vopros']}\n\n"
        f"──────────────\n"
        f"💬 Написать свою ситуацию анонимно: @{bot.token.split(':')[0]}_bot"
    )
    
    if CHANNEL_ID:
        try:
            await bot.send_message(CHANNEL_ID, post_text, parse_mode="Markdown")
            await callback.message.answer(f"📢 Пост успешно опубликован в канал {CHANNEL_ID}!")
        except Exception as e:
            await callback.message.answer(f"❌ Ошибка публикации в канал: {e}\n\nВот готовый текст для ручной вставки:\n\n{post_text}")
    else:
        await callback.message.answer(f"📢 Канал не указан в настройках. Вот готовый текст поста для публикации:\n\n{post_text}")
    await callback.answer()

# --- Подтверждение оплаты и начисление подписки ---

@router.callback_query(F.data.startswith("pay_appr_sub:"))
async def approve_subscription(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        return
    parts = callback.data.split(":")
    payment_id, target_user_id = int(parts[1]), int(parts[2])
    
    end_date = await db.add_subscription(target_user_id, days=30, reviews=3)
    date_str = end_date.strftime("%d.%m.%Y")
    
    user_confirm_text = (
        f"Принято, ты в списке до *{date_str}*. У тебя три разбора в месяц: "
        f"присылай анкету через бота (/anketa), как обычно, — отвечу в течение 48 часов. "
        f"Каждую принятую анкету я отмечаю: 1/3, 2/3, 3/3. Неиспользованные разборы на следующий месяц не переносятся."
    )
    try:
        await bot.send_message(target_user_id, user_confirm_text, parse_mode="Markdown")
        await callback.message.edit_caption(
            caption=callback.message.caption + f"\n\n✅ *ОДОБРЕНО: Подписка активна до {date_str} (3 разбора)*"
        )
    except Exception as e:
        await callback.message.answer(f"Ошибка отправки пользователю: {e}")
    await callback.answer()

@router.callback_query(F.data.startswith("pay_appr_single:"))
async def approve_single(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        return
    parts = callback.data.split(":")
    payment_id, target_user_id = int(parts[1]), int(parts[2])
    
    end_date = await db.add_subscription(target_user_id, days=30, reviews=1)
    
    user_confirm_text = (
        "Оплата разового разбора подтверждена! Присылай анкету через команду /anketa — "
        "она пойдёт в работу в первую очередь с гарантированным ответом до 48 часов."
    )
    try:
        await bot.send_message(target_user_id, user_confirm_text, parse_mode="Markdown")
        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n✅ *ОДОБРЕНО: Разовый разбор начислен.*"
        )
    except Exception as e:
        await callback.message.answer(f"Ошибка отправки пользователю: {e}")
    await callback.answer()

@router.callback_query(F.data.startswith("pay_rej:"))
async def reject_payment(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        return
    parts = callback.data.split(":")
    payment_id, target_user_id = int(parts[1]), int(parts[2])
    
    try:
        await bot.send_message(
            target_user_id,
            "К сожалению, платёж не подтверждён. Если произошла ошибка, проверь реквизиты или напиши автору."
        )
        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n❌ *ОТКЛОНЕНО*"
        )
    except Exception as e:
        await callback.message.answer(f"Ошибка отправки: {e}")
    await callback.answer()
