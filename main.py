import json
import re
from collections import Counter

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

import database
import menus
from conversations import quiz_conversation

# Твой токен
BOT_TOKEN = "7251803941:AAE0zAGT-1Aq2xa1VtVsO7MpdgWD_V5ved8"

functions = {}
start_func_name = ""

def build_buttons(data):
    # buttons_data — список словарей с кнопками из JSON
    keyboard = []
    for btn in data["args"].get("buttons"):

         # Кнопка с текстом и callback_data или URL (зависит от задачи)
        keyboard.append([InlineKeyboardButton(text=btn["text"], callback_data=btn.get("function"))])
    return InlineKeyboardMarkup(keyboard)

def high_level_function_parser(app, data):

    if data["type"] == "get":
        args = data["args"]
        get_type = args["type"].lower()

        # if get_type == "start_param":
        #     functions[args["request_func"]

        # Обработка команды /command
        if get_type == "command":
            if args["commandName"] == "start":
                global start_func_name
                start_func_name = args["requestFunc"]

            else:
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
            reply_markup = build_buttons(data) if buttons else None

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

        for test in config["tests"]:
            async def start(update, context):
                start_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="Начать", callback_data=test["name"] + "_next")]])

                context.user_data[test["name"]] = {
                    "questions": 1,
                    "answers": [],
                    "current": 0
                }

                if update.message:
                    await update.message.reply_text(test["welcome_text"], reply_markup=start_markup)
                elif update.callback_query:
                    await update.callback_query.answer()  # необязательно, но желательно
                    await update.callback_query.edit_message_text(test["welcome_text"], reply_markup=start_markup)

            functions[test["name"] + "_start"] = start

            app.add_handler(CallbackQueryHandler(functions[test["name"] + "_start"], pattern=test["name"] + "_start"))

            async def next(update, context):
                await update.callback_query.answer()
                splitted = update.callback_query.data.split(":")
                if len(splitted) > 1:
                    answer_code = splitted[1]
                    context.user_data[test["name"]]["answers"].append(answer_code)
                current = context.user_data[test["name"]]["current"]
                current += 1
                context.user_data[test["name"]]["current"] = current

                if current > len(test["questions"]):
                    answers = context.user_data[test["name"]]["answers"]
                    most_common = Counter(answers).most_common(1)[0][0]
                    result_text = test["results"].get(most_common, "Что-то пошло не так 😅")

                    finish_markup = InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Назад", callback_data=test["back_menu"])]])
                    return await update.callback_query.edit_message_text(result_text + "\n"+ test["finish_text"], reply_markup=finish_markup)


                question = test["questions"][current-1]

                buttons = [
                    [InlineKeyboardButton(option["text"], callback_data=test["name"]+ "_next" + ":" + option["key"])]
                    for option in question["options"]
                ]
                markup = InlineKeyboardMarkup(buttons)

                await update.callback_query.edit_message_text(question["question"], reply_markup=markup)

            functions[test["name"] + "_next"] = next
            app.add_handler(CallbackQueryHandler(functions[test["name"] + "_next"], pattern="^"+test["name"] + "_next"))

        for function in config["funcs"]:
            if function["abstraction"] == "high":
                high_level_function_parser(app, function)

    if start_func_name != "":
        async def start(update, context):
            if context.args:
                param = context.args[0]
                if param.startswith("qr_"):
                    print(param)
            else:
                await functions[start_func_name](update, context)

        app.add_handler(CommandHandler('start', start))

    app.run_polling()

if __name__ == '__main__':
    main()
