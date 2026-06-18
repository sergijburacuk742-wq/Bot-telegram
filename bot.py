import telebot
from telebot import types

# 1. ТУТ ВСТАВ СВІЙ ТОКЕН ВІД BOTFATHER
TOKEN = '8991892625:AAHbn2GyHZfbYxRjvIc8YRQIuHn2SJN6PYs'

# 2. ТУТ ВСТАВ СВІЙ TELEGRAM ID (щоб бот знав, куди скидати анкети)
# Щоб дізнатися свій ID, напиши в пошуку Telegram боту @getmyid_bot
ADMIN_ID = '1398283704'

bot = telebot.TeleBot(TOKEN)

# Словник для збереження відповідей користувачів
users_data = {}


# --- КРОК 1: КОМАНДА /START ---
@bot.message_handler(commands=['start'])
def start_message(message):
    # Створюємо клавіатуру з однією великою кнопкою
    markup = types.InlineKeyboardMarkup()
    btn_start = types.InlineKeyboardButton(text="📝 Подати заявку", callback_data="start_survey")
    markup.add(btn_start)

    # Формуємо текст нашої "першої сторінки"
    text = (
        "🦁 *LION TRAFFIC* 🦁\n\n"
        "Вітаємо! Ми шукаємо амбітних людей для заливу трафіку.\n"
        "Щоб приєднатися до команди, заповни коротку анкету."
    )

    # Відправляємо стартове повідомлення
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")


# --- ОБРОБКА ВСІХ INLINE-КНОПОК ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id

    # Якщо натиснули "Розпочати анкету"
    if call.data == "start_survey":
        users_data[chat_id] = {}  # Створюємо порожню анкету для користувача

        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_yes = types.InlineKeyboardButton("✅ Так", callback_data="exp_yes")
        btn_no = types.InlineKeyboardButton("❌ Ні", callback_data="exp_no")
        markup.add(btn_yes, btn_no)

        bot.edit_message_text("1️⃣ **Чи є досвід в арбітражі?**", chat_id, call.message.message_id, reply_markup=markup,
                              parse_mode="Markdown")

    # Якщо відповіли на питання про досвід
    elif call.data.startswith("exp_"):
        users_data[chat_id]['experience'] = "Так" if call.data == "exp_yes" else "Ні"

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📱 TikTok", callback_data="src_tiktok"),
            types.InlineKeyboardButton("▶️ YouTube Shorts", callback_data="src_yt"),
            types.InlineKeyboardButton("📸 Instagram", callback_data="src_inst"),
            types.InlineKeyboardButton("🤷‍♂️ Немає / Інше", callback_data="src_other")
        )
        bot.edit_message_text("2️⃣ **З якими джерелами працював?**", chat_id, call.message.message_id,
                              reply_markup=markup, parse_mode="Markdown")

    # Якщо відповіли на питання про джерела
    elif call.data.startswith("src_"):
        sources = {
            "src_tiktok": "TikTok",
            "src_yt": "YouTube Shorts",
            "src_inst": "Instagram",
            "src_other": "Немає / Інше"
        }
        users_data[chat_id]['source'] = sources[call.data]

        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("⏳ 1-3 години", callback_data="time_1_3"),
            types.InlineKeyboardButton("⏳ 3-6 годин", callback_data="time_3_6"),
            types.InlineKeyboardButton("🔥 Більше 6 годин", callback_data="time_6_plus")
        )
        bot.edit_message_text("3️⃣ **Скільки часу готовий приділяти в день?**", chat_id, call.message.message_id,
                              reply_markup=markup, parse_mode="Markdown")

    # Якщо відповіли на питання про час
    elif call.data.startswith("time_"):
        times = {
            "time_1_3": "1-3 години",
            "time_3_6": "3-6 годин",
            "time_6_plus": "Більше 6 годин"
        }
        users_data[chat_id]['time'] = times[call.data]

        # Тут кнопки вже не потрібні, просимо ввести текст
        bot.edit_message_text("4️⃣ **Скільки тобі років?**\n*(Напиши цифрою у чат)*", chat_id, call.message.message_id,
                              parse_mode="Markdown")
        # Вказуємо боту чекати текстове повідомлення
        bot.register_next_step_handler(call.message, get_age)


# --- КРОК 4: ОТРИМАННЯ ВІКУ ---
def get_age(message):
    chat_id = message.chat.id
    users_data[chat_id]['age'] = message.text

    msg = bot.send_message(chat_id,
                           "5️⃣ **Чому саме арбітраж? Чого очікуєш від роботи з нами?**\n*(Напиши коротку відповідь)*",
                           parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_reason)


# --- КРОК 5: ОТРИМАННЯ ПРИЧИНИ ТА ВІДПРАВКА АДМІНУ ---
def get_reason(message):
    chat_id = message.chat.id
    users_data[chat_id]['reason'] = message.text

    data = users_data[chat_id]
    username = f"@{message.from_user.username}" if message.from_user.username else "Прихований юзернейм"

    # Формуємо повідомлення для адміна
    admin_text = (
        f"🚨 **НОВА АНКЕТА!** 🚨\n\n"
        f"👤 **Користувач:** {username}\n"
        f"💼 **Досвід:** {data['experience']}\n"
        f"🌐 **Джерело:** {data['source']}\n"
        f"⏱ **Час в день:** {data['time']}\n"
        f"🎂 **Вік:** {data['age']}\n"
        f"💭 **Чому арбітраж:** {data['reason']}"
    )

    # Відправляємо адміну
    try:
        bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
        # Дякуємо користувачу
        bot.send_message(chat_id,
                         "✅ **Дякуємо! Твоя анкета успішно відправлена.**\nМенеджер перевірить її та зв'яжеться з тобою найближчим часом.",
                         parse_mode="Markdown")
    except Exception as e:
        bot.send_message(chat_id, "❌ Виникла помилка при відправці. Спробуйте пізніше.")
        print(f"Помилка відправки адміну: {e}")


# Запуск бота
if __name__ == '__main__':
    print("Бот-рекрутер успішно запущено!")
    bot.infinity_polling()