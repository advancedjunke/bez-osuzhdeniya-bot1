from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import SBP_REQUISITES, ADMIN_IDS, save_admin_id
import database as db
import keyboards as kb

router = Router()

class AnketaStates(StatesGroup):
    waiting_for_situaciya = State()
    waiting_for_popytki = State()
    waiting_for_vopros = State()
    waiting_for_tema = State()

class PaymentStates(StatesGroup):
    waiting_for_receipt = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await db.upsert_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    
    # Если список админов пуст, первый пользователь становится админом
    if not ADMIN_IDS:
        save_admin_id(message.from_user.id)
        await message.answer(f"👑 Вы автоматически назначены главным администратором бота (ID: `{message.from_user.id}`). Вам доступна панель /admin.", parse_mode="Markdown")
    
    text = (
        "Привет! Это бот канала «Без осуждения».\n\n"
        "Здесь ты можешь изложить свои мысли и получить на них ответ в течение 48 часов лично от меня. "
        "Я человек, которому искренне нравится помогать другим в решении личных проблем любого характера — "
        "главное, чтобы они были моральными.\n\n"
        "Например: «В последнее время я чувствую себя тревожно...» — вопросы уверенности в себе, "
        "самочувствия, жизненных проблем и трудностей.\n\n"
        "Пиши о своих переживаниях не стесняясь. Со мной стесняться точно не нужно — "
        "ведь это только ограничивает и заставляет чувствовать себя некомфортно."
    )
    await message.answer(text, reply_markup=kb.start_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "back_to_menu")
async def cb_back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "Главное меню проекта *«Без осуждения»*.\n\n"
        "Выбери нужный раздел кнопками ниже:"
    )
    await callback.message.edit_text(text, reply_markup=kb.start_keyboard(), parse_mode="Markdown")
    await callback.answer()

@router.message(Command("whoami"))
@router.message(Command("about"))
@router.callback_query(F.data == "show_who_am_i")
async def show_who_am_i(event: Message | CallbackQuery):
    text = (
        "Я - человек который уже два года развивает свой мозг и эмпатию.Я жил в очень стрессовых для меня временах из-за чего мне пришлось стать умнее и научиться решать свои моральные проблемы.Я могу видеть жизнь человека от первого лица с помощью воображения и вживления в роль,я буквально думаю о решении вашей жизненной проблемы от вашего лица, как будто если бы я был вами.В платных разборах и закрытом сообществе вы платите не за инфоциганство - его здесь нет,вы платите за мою энергию потраченную на решение вашей проблемы - а на это тратится колоссальное количество энергии.К тому же мне нравится понимать что человек стал лучше жить из-за меня.Всем удачи в жизни,и нервничайте поменьше - в последнее время,в нашей стране это очень нужно.Удачи каждому кто это прочитал♥"
    )
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb.who_am_i_keyboard())
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb.who_am_i_keyboard())

@router.message(Command("pravila"))
@router.callback_query(F.data == "show_rules")
async def show_rules(event: Message | CallbackQuery):
    text = (
        "Три вещи, которые важно знать.\n\n"
        "*Первое:* я не беру ситуации с клинической депрессией и психиатрическими диагнозами — "
        "это работа врачей, и я не буду рисковать тобой.\n\n"
        "*Второе:* разбор может быть опубликован в канале анонимно и только с твоего согласия.\n\n"
        "*Третье:* бесплатный разбор не гарантирован — я разбираю истории, которые зацепили сильнее всего. "
        "Платный разбор всегда в очереди первым. Средний срок ответа — до 48 часов."
    )
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb.rules_keyboard(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb.rules_keyboard(), parse_mode="Markdown")

@router.message(Command("platno"))
@router.callback_query(F.data == "show_platno")
async def show_platno(event: Message | CallbackQuery):
    text = (
        "💎 *Гарантированный разбор и подписка*\n\n"
        "• *Гарантированный разбор — 1000 руб.:* полная проработка анкеты, ответ в течение 48 часов.\n\n"
        "• *Подписка — 1000 руб. в месяц:* в неё входят три разбора (по сути, три по цене одного), и твои анкеты всегда первые в очереди.\n\n"
        f"💳 *Как оплатить:*\n"
        f"Переведи сумму по СБП: `{SBP_REQUISITES}`\n"
        "Затем нажми кнопку ниже и пришли сюда скриншот или чек перевода. Я подтвержу, что ты в списке. "
        "Подписка действует 30 дней с момента оплаты."
    )
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb.platno_keyboard(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb.platno_keyboard(), parse_mode="Markdown")

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "Здесь можно анонимно прислать ситуацию и получить разбор без осуждения.\n\n"
        "/anketa — отправить свою проблему\n"
        "/about — кто я такой?\n"
        "/pravila — правила проекта\n"
        "/platno — гарантированный платный разбор и подписка\n"
        "/status — проверить статус своей подписки\n"
        "/start — главное меню"
    )
    await message.answer(text)

@router.message(Command("status"))
async def cmd_status(message: Message):
    sub = await db.get_active_subscription(message.from_user.id)
    if sub:
        text = (
            f"✅ *Ваша подписка активна*\n\n"
            f"• Использовано разборов: *{sub['reviews_used']}/{sub['reviews_total']}*\n"
            f"• Действует до: *{sub['end_date']} UTC*\n"
            f"Ваши анкеты обрабатываются в первую очередь с гарантией ответа до 48 часов."
        )
    else:
        text = (
            "У вас сейчас нет активной подписки.\n\n"
            "Вы можете отправить свою проблему бесплатно (/anketa) или оформить гарантированный разбор / подписку (/platno)."
        )
    await message.answer(text, parse_mode="Markdown")

# --- Сценарий заполнения анкеты ---

@router.message(Command("anketa"))
@router.callback_query(F.data == "start_anketa")
async def start_anketa_flow(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "📋 *Вопрос 1 из 4: Что происходит*\n\n"
        "Опиши, что происходит, с кем и как давно. Без долгой предыстории, но обязательно с эмоциями — это важно: то, как ты себя чувствуешь в этой ситуации, помогает раскрыть её суть.\n\n"
        "⚠️ *Лимит: 600 символов.* Если не влезает — попытайся убрать подробности, сохранив смысл."
    )
    await state.set_state(AnketaStates.waiting_for_situaciya)
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb.cancel_keyboard(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb.cancel_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "cancel_anketa")
async def cancel_anketa(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Заполнение анкеты отменено.", reply_markup=kb.start_keyboard())
    await callback.answer()

@router.message(AnketaStates.waiting_for_situaciya)
async def process_situaciya(message: Message, state: FSMContext):
    if len(message.text) > 600:
        await message.answer(
            f"Твой текст содержит {len(message.text)} символов (лимит — 600).\n"
            "Пожалуйста, попытайся убрать подробности, сохранив смысл, и пришли его снова:"
        )
        return
    await state.update_data(situaciya=message.text)
    await state.set_state(AnketaStates.waiting_for_popytki)
    text = (
        "📋 *Вопрос 2 из 4: Что уже пробовалось*\n\n"
        "Что ты уже пробовал(а) делать и почему, как тебе кажется, это не сработало? "
        "К каким выводам или чувствам ты пришёл(ла)?\n\n"
        "⚠️ *Лимит: 300 символов.* Это важно, чтобы понять, в какую стену ты упираешься, и не предлагать тебе банальных очевидных вещей."
    )
    await message.answer(text, reply_markup=kb.cancel_keyboard(), parse_mode="Markdown")

@router.message(AnketaStates.waiting_for_popytki)
async def process_popytki(message: Message, state: FSMContext):
    if len(message.text) > 300:
        await message.answer(
            f"Твой текст содержит {len(message.text)} символов (лимит — 300).\n"
            "Пожалуйста, выдели главные попытки и чувства, сохранив смысл, и пришли снова:"
        )
        return
    await state.update_data(popytki=message.text)
    await state.set_state(AnketaStates.waiting_for_vopros)
    text = (
        "📋 *Вопрос 3 из 4: Главный вопрос*\n\n"
        "Какой один главный вопрос сейчас не даёт тебе покоя? Сформулируй его одним предложением.\n\n"
        "⚠️ *Лимит: до 150 символов.*"
    )
    await message.answer(text, reply_markup=kb.cancel_keyboard(), parse_mode="Markdown")

@router.message(AnketaStates.waiting_for_vopros)
async def process_vopros(message: Message, state: FSMContext):
    if len(message.text) > 150:
        await message.answer(
            f"Вопрос содержит {len(message.text)} символов (лимит — 150).\n"
            "Пожалуйста, сформулируй главный вопрос одним коротким предложением:"
        )
        return
    await state.update_data(vopros=message.text)
    await state.set_state(AnketaStates.waiting_for_tema)
    text = (
        "📋 *Вопрос 4 из 4: Категория*\n\n"
        "Последний шаг — выбери тему кнопкой ниже:"
    )
    await message.answer(text, reply_markup=kb.topics_keyboard(), parse_mode="Markdown")

@router.callback_query(AnketaStates.waiting_for_tema, F.data.startswith("tema:"))
async def process_tema(callback: CallbackQuery, state: FSMContext, bot: Bot):
    tema = callback.data.split(":", 1)[1]
    data = await state.get_data()
    await state.clear()
    
    user_id = callback.from_user.id
    username = callback.from_user.username or ""
    first_name = callback.from_user.first_name or ""
    await db.upsert_user(user_id, username, first_name)
    
    # Проверяем подписку
    sub = await db.get_active_subscription(user_id)
    is_subscriber = False
    usage_info = ""
    if sub and sub["reviews_used"] < sub["reviews_total"]:
        is_subscriber = True
        used, total = await db.use_subscription_review(user_id)
        usage_info = f" (Платный подписчик, разбор {used}/{total})"

    sub_id = await db.save_submission(
        user_id=user_id,
        situaciya=data["situaciya"],
        popytki=data["popytki"],
        vopros=data["vopros"],
        tema=tema,
        is_subscriber=is_subscriber
    )

    final_text = (
        "Готово, твоя ситуация у меня. Если история зацепит — в течение 48 часов придёт разбор, "
        "и я предложу опубликовать его в канале анонимно.\n\n"
        "Если нужен гарантированный платный разбор — нажми кнопку ниже."
    )
    await callback.message.edit_text(final_text, reply_markup=kb.final_anketa_keyboard())
    await callback.answer()

    import html
    # Уведомляем администратора
    priority_badge = "🔥 <b>ПЛАТНЫЙ ПОДПИСЧИК</b>" if is_subscriber else "⚪ <b>Бесплатная анкета</b>"
    clean_username = f"@{html.escape(username)}" if username else "без_юзернейма"
    admin_alert = (
        f"{priority_badge}{html.escape(usage_info)}\n"
        f"📝 <b>Новая проблема #{sub_id}</b>\n"
        f"От: {clean_username} (ID: <code>{user_id}</code>)\n"
        f"🏷 Тема: <b>{html.escape(tema)}</b>\n\n"
        f"<b>1. Что происходит:</b>\n{html.escape(data['situaciya'])}\n\n"
        f"<b>2. Что пробовал(а):</b>\n{html.escape(data['popytki'])}\n\n"
        f"<b>3. Главный вопрос:</b>\n{html.escape(data['vopros'])}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                admin_alert,
                reply_markup=kb.admin_submission_keyboard(sub_id, user_id),
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Error sending submission to admin {admin_id}: {e}")

# --- Сценарий отправки чека оплаты ---

@router.callback_query(F.data == "send_receipt")
async def start_send_receipt(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PaymentStates.waiting_for_receipt)
    text = (
        "📸 Отправь сюда скриншот или документ с подтверждением перевода по СБП.\n"
        "Я сразу передам его автору проекта на подтверждение."
    )
    await callback.message.answer(text, reply_markup=kb.cancel_keyboard())
    await callback.answer()

@router.message(PaymentStates.waiting_for_receipt, F.photo | F.document)
async def process_receipt(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    user_id = message.from_user.id
    username = message.from_user.username or ""
    
    payment_id = await db.save_payment(user_id, username, file_id)
    
    await message.answer(
        "Чек получен! Я передал его автору на подтверждение. "
        "Как только оплата будет подтверждена, тебе придёт уведомление с условиями подписки.",
        reply_markup=kb.start_keyboard()
    )

    admin_caption = (
        f"💳 <b>Новый чек на проверку #{payment_id}</b>\n"
        f"От: @{html.escape(username) if username else 'без_юзернейма'} (ID: <code>{user_id}</code>)\n\n"
        f"Выбери действие для начисления:"
    )
    for admin_id in ADMIN_IDS:
        try:
            if message.photo:
                await bot.send_photo(
                    admin_id,
                    photo=file_id,
                    caption=admin_caption,
                    reply_markup=kb.admin_payment_keyboard(payment_id, user_id),
                    parse_mode="HTML"
                )
            else:
                await bot.send_document(
                    admin_id,
                    document=file_id,
                    caption=admin_caption,
                    reply_markup=kb.admin_payment_keyboard(payment_id, user_id),
                    parse_mode="HTML"
                )
        except Exception as e:
            print(f"Error sending payment to admin {admin_id}: {e}")
