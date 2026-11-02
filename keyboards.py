from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Отправить свою проблему", callback_data="start_anketa")],
        [InlineKeyboardButton(text="👤 Кто я такой?", callback_data="show_who_am_i")],
        [InlineKeyboardButton(text="📖 Сначала правила", callback_data="show_rules")],
        [InlineKeyboardButton(text="💎 Гарантированный разбор / подписка", callback_data="show_platno")]
    ])

def who_am_i_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Отправить свою проблему", callback_data="start_anketa")],
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
    ])

def rules_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Отправить свою проблему", callback_data="start_anketa")],
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
    ])

def topics_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1. Дисциплина и мотивация", callback_data="tema:Дисциплина и мотивация")],
        [InlineKeyboardButton(text="2. Отношения и зависимость", callback_data="tema:Отношения и зависимость")],
        [InlineKeyboardButton(text="3. Жизненный тупик и решение", callback_data="tema:Жизненный тупик и решение")],
        [InlineKeyboardButton(text="4. Личное, не с кем обсудить", callback_data="tema:Личное, не с кем обсудить")]
    ])

def final_anketa_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Гарантированный разбор", callback_data="show_platno")],
        [InlineKeyboardButton(text="◀️ В главное меню", callback_data="back_to_menu")]
    ])

def platno_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Отправить чек / скриншот", callback_data="send_receipt")],
        [InlineKeyboardButton(text="◀️ В главное меню", callback_data="back_to_menu")]
    ])

def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить заполнение", callback_data="cancel_anketa")]
    ])

def admin_submission_keyboard(sub_id: int, user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Ответить автору", callback_data=f"adm_reply:{sub_id}:{user_id}")
        ],
        [
            InlineKeyboardButton(text="📢 В канал (анонимно)", callback_data=f"adm_pub:{sub_id}")
        ]
    ])

def admin_payment_keyboard(payment_id: int, user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить подписку (30 дней, 3 разбора)", callback_data=f"pay_appr_sub:{payment_id}:{user_id}")
        ],
        [
            InlineKeyboardButton(text="✅ Одобрить разовый разбор (1 разбор)", callback_data=f"pay_appr_single:{payment_id}:{user_id}")
        ],
        [
            InlineKeyboardButton(text="❌ Отклонить платёж", callback_data=f"pay_rej:{payment_id}:{user_id}")
        ]
    ])
