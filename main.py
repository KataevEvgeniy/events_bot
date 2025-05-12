from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

import database
import menus
from conversations import quiz_conversation

# Твой токен
BOT_TOKEN = "7251803941:AAE0zAGT-1Aq2xa1VtVsO7MpdgWD_V5ved8"


def main():
    database.init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()


    #Обработчики команд
    app.add_handler(CommandHandler('start', menus.main_menu))
    app.add_handler(CommandHandler('admin', menus.admin_menu))

    #Обработчики меню
    app.add_handler(CallbackQueryHandler(menus.main_menu_button_handler, pattern="^main_menu_"))
    app.add_handler(CallbackQueryHandler(menus.possibilities_menu_button_handler, pattern="^possibilities_"))
    app.add_handler(CallbackQueryHandler(menus.admin_menu_button_handler,pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(menus.store_menu_button_handler,pattern="^store_"))


    #Обработчики кнопок модульного меню
    app.add_handler(CallbackQueryHandler(menus.back_keyboard_handler,pattern="^back_to_"))


    #Обработчики диалогов
    app.add_handler(quiz_conversation())


    app.run_polling()

if __name__ == '__main__':
    main()
