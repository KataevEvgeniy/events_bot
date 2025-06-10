import json
import re

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

import database
import menus
from conversations import quiz_conversation

# Твой токен
BOT_TOKEN = "7251803941:AAE0zAGT-1Aq2xa1VtVsO7MpdgWD_V5ved8"

functions = {}

def build_buttons(buttons_data):
    # buttons_data — список словарей с кнопками из JSON
    keyboard = []
    for btn in buttons_data:
        # Кнопка с текстом и callback_data или URL (зависит от задачи)
        keyboard.append([InlineKeyboardButton(text=btn["text"], callback_data=btn.get("function"))])
    return InlineKeyboardMarkup(keyboard)

def high_level_function_parser(app, data):

    if data["type"] == "get":
        args = data["args"]
        get_type = args["type"].lower()

        # Обработка команды /command
        if get_type == "command":
            app.add_handler(CommandHandler(args["commandName"], functions[args["requestFunc"]]))

        # Обработка callback по шаблону
        elif get_type == "callback":
            pattern = args["pattern"]
            app.add_handler(CallbackQueryHandler(functions[args["requestFunc"]], pattern=pattern))

    elif data["type"] == "send":
        args = data["args"]
        msg_type = args["type"].lower()

        # Текстовые сообщения с кнопками
        if msg_type == "text":
            buttons = args.get("buttons")
            reply_markup = build_buttons(buttons) if buttons else None

            async def send_text(update, context):
                if update.message:
                    await update.message.reply_text(args["text"], reply_markup=reply_markup)
                elif update.callback_query:
                    await update.callback_query.answer()  # необязательно, но желательно
                    await update.callback_query.edit_message_text(args["text"], reply_markup=reply_markup)

            functions[data["name"]] = send_text

        # Сообщение с изображением
        elif msg_type == "image":
            text = args.get("text", "")
            image_url = args.get("image")

            async def send_image(update, context):
                if update.message:
                    await update.message.reply_photo(photo=image_url, caption=text)
                elif update.callback_query:
                    await update.callback_query.answer()
                    await update.callback_query.message.reply_photo(photo=image_url, caption=text)

            functions[data["name"]] = send_image




def main():
    database.init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    with open("C:\\Users\\jackm\\Documents\\config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)

        for function in config["funcs"]:
            if function["abstraction"] == "high":
                high_level_function_parser(app, function)


    # #Обработчики команд
    # app.add_handler(CommandHandler('start', menus.main_menu))
    # app.add_handler(CommandHandler('admin', menus.admin_menu))
    #
    # #Обработчики меню
    # app.add_handler(CallbackQueryHandler(menus.main_menu_button_handler, pattern="^main_menu_"))
    # app.add_handler(CallbackQueryHandler(menus.possibilities_menu_button_handler, pattern="^possibilities_"))
    # app.add_handler(CallbackQueryHandler(menus.admin_menu_button_handler,pattern="^admin_"))
    # app.add_handler(CallbackQueryHandler(menus.store_menu_button_handler,pattern="^store_"))
    #
    #
    # #Обработчики кнопок модульного меню
    # app.add_handler(CallbackQueryHandler(menus.back_keyboard_handler,pattern="^back_to_"))
    #
    #
    # app.add_handler(CallbackQueryHandler(menus.dice_menu_button_handler, pattern="^dice_"))
    #
    # #Обработчики диалогов
    # app.add_handler(quiz_conversation())


    app.run_polling()

if __name__ == '__main__':
    main()
