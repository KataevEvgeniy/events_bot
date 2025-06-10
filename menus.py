import asyncio
import random
import string

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import database
import messages
import store


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
        [InlineKeyboardButton('📸 Отсканируй QR-коды и получи приз', callback_data='possibilities_qr_quest')],
        [InlineKeyboardButton('🎰 Рулетка на призы', callback_data='possibilities_roulette')]
        # [InlineKeyboardButton('📚 Викторина о колледже', callback_data='possibilities_college_quiz')], #TODO: Создать вопросы как в квизе выше, но про колледж и исходя из qr кодов
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
    elif data == 'possibilities_qr_quest':
        await query.edit_message_text(
            "🎯 *Задание для тебя!*\n\n"
            "📸 Прогуляйся по мероприятию, отсканируй все QR-коды и познакомься с историей колледжа!\n"
            "🎁 Когда справишься — тебя ждёт викторина и шанс получить *много звезд*! 💥\n"
            "👍 Их можно обменять на ценные призы!",
            parse_mode="Markdown",
            reply_markup=back_keyboard("possibilities_menu")
        )
    elif data == 'possibilities_roulette':
        await dice_menu(update,context)


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
# DICE MENU
#-----------------------------------------------------------------------------------------------------------------------

def dice_menu_keyboard(is_free:bool):
    keyboard = [
        [InlineKeyboardButton(f"🎰 Испытать удачу {'бесплатно' if is_free else '1 ⭐'}", callback_data="dice_throw")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def dice_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = database.get_user(update.effective_user.id)
    if update.message:
        await update.message.reply_text("Испытай свою удачу и выиграй приз", reply_markup=dice_menu_keyboard(user.free_spin))
    elif update.callback_query:
        query = update.callback_query
        await query.edit_message_text("Испытай свою удачу и выиграй приз", reply_markup=dice_menu_keyboard(user.free_spin))

async def dice_menu_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == 'dice_throw':
        telegram_id = update.effective_user.id


        user = database.get_user(telegram_id)
        if not user.free_spin:
            if user.count_stars == 0:
                await query.answer("Недостаточно звёзд 😕", show_alert=True)
                return
            else:
                store.remove_stars(telegram_id, 1)
        else:
            database.update_user(telegram_id, user.is_admin, user.count_stars, user.is_apocalypse_quiz_complete, False)

        data = await query.message.reply_dice(emoji="🎰")

        await asyncio.sleep(3)

        # Расшифровка значения
        value = data.dice.value


        if value == 64:
            store.add_stars(telegram_id, 7)
            await query.message.reply_text("🎉 Поздравляем! Вы выиграли 7 ⭐ звёзд! Выпало 777! 🎰",reply_markup=dice_menu_keyboard(False))
        elif value in {16, 32, 48}:
            store.add_stars(telegram_id, 3)
            await query.message.reply_text("🎉 Поздравляем! Вы выиграли 3 ⭐ звезды! Первые две семёрки!",reply_markup=dice_menu_keyboard(False))
        elif value in {1, 22, 43}:
            store.add_stars(telegram_id, 3)
            await query.message.reply_text("🎉 Поздравляем! Вы выиграли 3 ⭐ звезды! Выпало три одинаковых символа!",reply_markup=dice_menu_keyboard(False))
        else:
            await query.message.reply_text(f"Не повезло!",reply_markup=dice_menu_keyboard(False))

        # Закрываем индикатор загрузки кнопки
        await query.answer()


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

