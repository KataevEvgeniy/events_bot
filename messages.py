import menus
from Schedule import Schedule, Event


async def main_menu_info(query):
    text = ("📚 **Екатеринбургский экономико-технологический колледж (ЕЭТК)** — одно из старейших и крупнейших профессиональных учебных заведений Урала, основанное в 1932 году.\n\n" 
        "🏆 Колледж — лауреат конкурса «100 лучших образовательных учреждений России» и победитель конкурса «100 лучших товаров и услуг». "
        "Имеет сертификат качества ISO 9001:2008.\n\n"
        "🎓 Около 2500 студентов обучаются по 15 образовательным программам. "
        "Выпускники успешно работают в экономике региона.\n\n"
        "📍 Адрес: г. Екатеринбург, ул. Декабристов, 58\n"
        "🌐 Сайт: [eetk.ru](http://eetk.ru/)")
    await query.edit_message_text(text, parse_mode='Markdown',reply_markup=menus.back_keyboard("main_menu"))

async def main_menu_schedule(query):
    schedule = Schedule([
        Event("10:00", "Экскурсия по колледжу", "Познакомимся с учебными аудиториями, лабораториями и мастерскими."),
        Event("11:00", "Презентация специальностей",
              "Расскажем о направлениях обучения и перспективах трудоустройства."),
        Event("12:00", "Мастер-классы от преподавателей", "Попробуйте себя в профессии уже сегодня!")])
    await query.edit_message_text(schedule.format_schedule(), parse_mode='Markdown',reply_markup=menus.back_keyboard("main_menu"))

async def main_menu_virtual_tour(query):
    await query.edit_message_text("🌐 Виртуальная экскурсия: [Смотреть тур](https://example.com)",reply_markup=menus.back_keyboard("main_menu"))



QR_ARTICLES = [
    ("pxmd", "О колледже"),
    ("cinr", "О специальностях"),
    ("ndoi", "Про жизнь")
]

async def qr_article_links(query):
    base_url = "https://t.me/eetkEventBot?start=qr_"
    message = "*📚 Статьи:*\n\n"

    for code, title in QR_ARTICLES:
        message += f"{title} — `{base_url}{code}`\n"

    message += (
        "\n📱 *Хочешь поделиться статьёй офлайн?*\n"
        "Сгенерируй QR-код для любой ссылки на одном из этих сайтов:\n"
        "• [qrcode-tiger.com](https://www.qrcode-tiger.com)\n"
        "• [qr.io](https://qr.io/)\n"
        "• [qrcode-monkey.com](https://www.qrcode-monkey.com/)\n\n"
        "_Просто вставь нужную ссылку — и получишь готовый код для печати или отправки._"
    )

    await query.edit_message_text(message, parse_mode='Markdown',disable_web_page_preview=True)

async def about_college(update, context):
    if context.args:
        param = context.args[0]

        if param == "qr_"+QR_ARTICLES[0][0]:
            await update.message.reply_photo(
                photo="https://avatars.mds.yandex.net/get-altay/4441482/2a0000017758d6ed70cd88390d3569474cd8/XXXL",
                caption=(
                    "🎓 *Хочешь знать, что за место этот ЕЭТК?*\n\n"
                    "Когда я впервые пришёл сюда, думал — ну обычный колледж. А оказалось, тут реально крутая атмосфера. "
                    "Колледжу больше 80 лет, и это не просто цифра — тут всё пропитано историей и традициями. "
                    "При этом всё по-современному: классные преподаватели, много практики и всё, что нужно для учёбы.\n\n"
                    "Даже не думал, что мне тут так понравится. За каждым углом что-то происходит: выставки, конкурсы, мероприятия. "
                    "А ещё директор — не просто начальник, а человек, который реально в теме. Короче, если хочешь не просто «отсидеться», а чему-то научиться — тебе сюда."
                ),
                parse_mode='Markdown'
            )

        elif param == "qr_"+QR_ARTICLES[1][0]:
            await update.message.reply_photo(
                photo="http://eetk.ru/wp-content/uploads/2011/11/1-300x300.jpg",
                caption=(
                    "💼 *Про специальности простыми словами*\n\n"
                    "Я учусь на «Прикладной информатике» — и, честно, это круто. Но вообще здесь много интересных направлений: "
                    "от гостиничного сервиса до холодильных установок (да, звучит необычно, но востребовано!).\n\n"
                    "У нас никто не тянет до 4 курса без дела — уже на втором начинаешь что-то уметь. "
                    "Есть практика, реальный опыт, иногда даже можно подработку найти через колледж. "
                    "Преподы — адекватные, многие сами в индустрии варятся, так что рассказывают не «по бумажке», а по-настоящему."
                ),
                parse_mode='Markdown'
            )

        elif param == "qr_"+QR_ARTICLES[2][0]:
            await update.message.reply_photo(
                photo="https://sun9-14.userapi.com/impg/n44aL0pckvsf7q1ym2-Ww9uOHgasae6gzkmKrA/by8yVQlaZ60.jpg?size=2560x1707&quality=95&sign=e06d32d84920aa683c2d4a2b04d85ef2&type=album",
                caption=(
                    "🎉 *Как у нас тут живётся*\n\n"
                    "Скажу честно — думал, что колледж это не только пара-дом. А тут столько движухи, что устаёшь выбирать. "
                    "У нас проходят всякие конкурсы, спортклубы, концерты. Я, например, сначала просто пришёл на кибертурнир, а потом втянулся в медиацентр. "
                    "Теперь и учусь, и ролики монтирую для мероприятий.\n\n"
                    "Колледж реально поощряет активность — грамоты, поездки, даже премии бывают. "
                    "Так что если тебе хочется не только учиться, но и жить интересно — здесь скучно точно не будет."
                ),
                parse_mode='Markdown'
            )