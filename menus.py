import random
import string

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import database
import messages


#-----------------------------------------------------------------------------------------------------------------------
# MAIN MENU
#-----------------------------------------------------------------------------------------------------------------------

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton('ℹ Информация о колледже', callback_data='main_menu_info')],
        [InlineKeyboardButton('📅 Расписание мероприятий', callback_data='main_menu_schedule')],
        [InlineKeyboardButton('🌐 Магазин', callback_data='main_menu_store')],
        [InlineKeyboardButton('🧩 Интерактивы', callback_data='main_menu_interactive')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    database.add_user(telegram_id)
    user = database.get_user(telegram_id)

    max_stars_display = 15
    filled_stars = "⭐" * min(user.count_stars, max_stars_display)
    empty_stars = "☆" * (max_stars_display - min(user.count_stars, max_stars_display))

    message_text = (
        f"👋 Добро пожаловать на *День открытых дверей* нашего колледжа!\n\n"
        f"🌟 *Ваш рейтинг:*\n"
        f"{filled_stars}{empty_stars}  ({user.count_stars} звёзд)\n\n"
        f"Выберите действие ниже:"
    )

    if context.args:
        param = context.args[0]
        if param.startswith("qr_"):
            await messages.about_college(update,context)
    # обработка если вызов из сообщения
    elif update.message:
        await update.message.reply_text(message_text,reply_markup=main_menu_keyboard())
    # обработка если вызов из кнопки
    elif update.callback_query:
        query = update.callback_query

        await query.edit_message_text(message_text,reply_markup=main_menu_keyboard())




async def main_menu_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    data = query.data

    if data == 'main_menu_info':
        await messages.main_menu_info(query)
    elif data == 'main_menu_schedule':
        await messages.main_menu_schedule(query)
    elif data == 'main_menu_store':
        await store_menu(update,context)
    elif data == 'main_menu_interactive':
        await possibilities_menu(update,context)

#-----------------------------------------------------------------------------------------------------------------------
# POSSIBILITIES MENU
#-----------------------------------------------------------------------------------------------------------------------

def possibilities_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton('🎯 Квиз "Твоя специальность"', callback_data='start_quiz')],
        [InlineKeyboardButton('📚 Викторина о колледже', callback_data='possibilities_college_quiz')],
        [InlineKeyboardButton('🔓 Открой секреты колледжа', callback_data='possibilities_secrets')],
        [InlineKeyboardButton('📸 Отсканируй QR-коды и получи приз', callback_data='possibilities_qr_quest')],
        [InlineKeyboardButton('🎰 Рулетка на призы', callback_data='possibilities_roulette')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def possibilities_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # обработка если вызов из сообщения
    if update.message:
        await update.message.reply_text("🎮 Выберите интерактив:",reply_markup=modular_keyboard([possibilities_menu_keyboard(),back_keyboard("main_menu")]))
    # обработка если вызов из кнопки
    elif update.callback_query:
        query = update.callback_query

        await query.edit_message_text("🎮 Выберите интерактив:",reply_markup=modular_keyboard([possibilities_menu_keyboard(),back_keyboard("main_menu")]))

async def possibilities_menu_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    data = query.data


    if data == 'possibilities_college_quiz':
        await query.edit_message_text("📚 Викторина о колледже скоро начнётся!")
    elif data == 'possibilities_secrets':
        await query.edit_message_text("🔓 Секрет колледжа: наши студенты побеждают на олимпиадах каждый год!")
    elif data == 'possibilities_qr_quest':
        await query.edit_message_text("📸 Отсканируйте все QR-коды на мероприятии и получите подарок!")
    elif data == 'possibilities_roulette':
        await query.edit_message_text("🎰 Запусти рулетку и выиграй призы! Попытка доступна каждые 5 минут.")


#-----------------------------------------------------------------------------------------------------------------------
# STORE MENU
#-----------------------------------------------------------------------------------------------------------------------

def store_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton('🎓 Значок колледжа — 2⭐', callback_data='store_pin')],
        [InlineKeyboardButton('🖊️ Фирменная ручка — 3⭐', callback_data='store_pen')],
        [InlineKeyboardButton('🧢 Бейсболка с логотипом — 5⭐', callback_data='store_cap')],
        [InlineKeyboardButton('🎒 Рюкзак ЕЭТК — 8⭐', callback_data='store_backpack')],
        [InlineKeyboardButton('🎁 Сюрприз-бокс — 10⭐', callback_data='store_box')],
    ]
    return InlineKeyboardMarkup(keyboard)


async def store_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "🛍 Добро пожаловать в магазин колледжа!\nВыберите товар, который хотите приобрести:",
            reply_markup=modular_keyboard([store_menu_keyboard(),back_keyboard("main_menu")])
        )
    elif update.callback_query:
        query = update.callback_query
        await query.edit_message_text(
            "🛍 Добро пожаловать в магазин колледжа!\nВыберите товар, который хотите приобрести:",
            reply_markup=modular_keyboard([store_menu_keyboard(),back_keyboard("main_menu")])
        )

async def store_menu_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    telegram_id = query.from_user.id
    user = database.get_user(telegram_id)

    store_items = {
        "store_pin":  {"name": "Значок колледжа", "cost": 2},
        "store_pen":  {"name": "Фирменная ручка", "cost": 3},
        "store_cap":  {"name": "Бейсболка с логотипом", "cost": 5},
        "store_backpack": {"name": "Рюкзак ЕЭТК", "cost": 8},
        "store_box": {"name": "Сюрприз-бокс", "cost": 10},
    }

    item = store_items.get(query.data)

    if item:
        if user.count_stars >= item["cost"]:
            redeem_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

            new_balance = user.count_stars - item["cost"]

            await query.edit_message_text(
                f"🎟 *Ваш код для получения товара:* `{redeem_code}`\n"
                f"📌 Покажите этот код продавцу.\n\n",
                parse_mode="Markdown",
                reply_markup=back_keyboard("main_menu")
            )
        else:
            await query.answer("Недостаточно звёзд 😕", show_alert=True)


#-----------------------------------------------------------------------------------------------------------------------
# ADMIN MENU
#-----------------------------------------------------------------------------------------------------------------------

def admin_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton('Создать QR код', callback_data='admin_qr')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Панель администратора",reply_markup=admin_menu_keyboard())

async def admin_menu_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    data = query.data

    if data == 'admin_qr':
        await messages.qr_article_links(query)

#-----------------------------------------------------------------------------------------------------------------------
# MODULAR KEYBOARD
#-----------------------------------------------------------------------------------------------------------------------

def modular_keyboard(keyboards: list[InlineKeyboardMarkup]):
    modular_keyboards = []

    for keyboard in keyboards:
        modular_keyboards += keyboard.inline_keyboard

    return InlineKeyboardMarkup(modular_keyboards)



#-----------------------------------------------------------------------------------------------------------------------
# BACK KEYBOARD
#-----------------------------------------------------------------------------------------------------------------------


def back_keyboard(param: str):
    keyboard = []

    if param == "main_menu":
        keyboard.append([InlineKeyboardButton('⬅️ Вернуться', callback_data='back_to_main_menu')])
    elif param == "possibilities_menu":
        keyboard.append([InlineKeyboardButton('⬅️ Вернуться', callback_data='back_to_possibilities_menu')])

    return InlineKeyboardMarkup(keyboard)

async def back_keyboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    data = query.data

    if data == 'back_to_possibilities_menu':
        await possibilities_menu(update,context)
    elif data == 'back_to_main_menu':
        await main_menu(update,context)

