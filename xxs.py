import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = "8536816040:AAFKCaBRuAx74DDZ25lQYeMjKtX5DvhrrSk"

passport_data = {}  # {chat_id: {user_id: [file_id, ...]}}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖Bot ishga tushdi! Passportlarni tashlang.")

# Обработка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat.id
    file_id = update.message.photo[-1].file_id  # уникальный ID фото

    # Создаём структуру
    if chat_id not in passport_data:
        passport_data[chat_id] = {}
    if user.id not in passport_data[chat_id]:
        passport_data[chat_id][user.id] = []

    # Проверяем дубликаты
    if file_id in passport_data[chat_id][user.id]:
        await update.message.reply_text(f"⚠️ {user.first_name}, uje tashalgan!")
        return

    passport_data[chat_id][user.id].append(file_id)
    await update.message.reply_text(
        f"📸 {user.first_name} jami tashagan pasporti: {len(passport_data[chat_id][user.id])}"
    )

# Команда /hisoblash — показать статистику по группе + общий итог
async def hisoblash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in passport_data or not passport_data[chat_id]:
        await update.message.reply_text("📊 Hali hechkim rasm tashamadi.")
        return

    text = "📊 Gruppaning statistikasi:\n\n"
    total = 0  # общая сумма паспортов

    for user_id, photos in passport_data[chat_id].items():
        user = await context.bot.get_chat_member(chat_id, user_id)
        count = len(photos)
        total += count
        text += f"👤 {user.user.first_name}: {count} dona rasm\n"

    text += f"\n📈 Ja'mi: {total} passport tashlandi."

    await update.message.reply_text(text)

# Команда /reset — очистить статистику
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    passport_data[chat_id] = {}
    await update.message.reply_text("♻️ Статистика сброшена!")

# Основная функция
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("hisoblash", hisoblash))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🤖 Бот запущен. Ждём сообщений...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
