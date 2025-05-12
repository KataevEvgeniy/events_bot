import random
from collections import Counter

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, filters, MessageHandler, ContextTypes, CallbackQueryHandler

import database
import menus
import post_apocalypse_test

#-----------------------------------------------------------------------------------------------------------------------
# POST APOCALYPSE QUIZ CONVERSATION
#-----------------------------------------------------------------------------------------------------------------------

QUIZ_STEP1 = range(1)

def quiz_conversation():
    return ConversationHandler(
        name="quiz_dialog",
        entry_points=[CallbackQueryHandler(quiz_conversation_start_handler, pattern="^start_quiz$")],
        states={
            QUIZ_STEP1: [CallbackQueryHandler(handle_answer)],
        },
        fallbacks=[],
    )

async def quiz_conversation_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Сейчас мы выберем тебе специальность в постапокалипсисе!")

    selected = random.sample(post_apocalypse_test.QUESTIONS, 7)
    context.user_data["quiz"] = {
        "questions": selected,
        "answers": [],
        "current": 0
    }

    return await send_next_question(update, context)


async def send_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quiz_data = context.user_data["quiz"]
    current = quiz_data["current"]
    if current >= len(quiz_data["questions"]):
        return await finish_quiz(update, context)

    question = quiz_data["questions"][current]

    buttons = [
        [InlineKeyboardButton(text, callback_data=code)]
        for code, text in question["options"]
    ]
    markup = InlineKeyboardMarkup(buttons)

    await update.callback_query.edit_message_text(question["question"], reply_markup=markup)
    return QUIZ_STEP1

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    answer_code = query.data

    context.user_data["quiz"]["answers"].append(answer_code)
    context.user_data["quiz"]["current"] += 1

    return await send_next_question(update, context)

async def finish_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answers = context.user_data["quiz"]["answers"]
    most_common = Counter(answers).most_common(1)[0][0]
    result_text = post_apocalypse_test.RESULTS.get(most_common, "Что-то пошло не так 😅")

    telegram_id = update.effective_user.id
    user = database.get_user(telegram_id)
    stars_text = ""
    if not user.is_apocalypse_quiz_complete:
        database.update_user(user.telegram_id,user.is_admin,user.count_stars + 3,True)
        stars_text = (
            f"🎉 Вы прошли тест и получили *3 звезды!*\n"
            f"⭐ Текущий рейтинг: {user.count_stars + 3} звёзд"
        )



    full_message = (
        f"🧬 *Результат теста:*\n{result_text}\n\n"
        f"{stars_text}"
    )

    await update.callback_query.edit_message_text(full_message, reply_markup=menus.back_keyboard("main_menu"))
    return ConversationHandler.END












QUIZ1_STEP1, QUIZ1_STEP2 = range(100,102)