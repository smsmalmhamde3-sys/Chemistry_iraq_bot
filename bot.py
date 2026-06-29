from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "ضع_التوكن_الجديد_هنا"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📝 اختبارات MCQ"],
        ["✅ حلول الواجبات"],
        ["❓ اسأل الأستاذة"],
        ["🏆 درجاتي"],
        ["ℹ️ عن البوت"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🧪 أهلاً بك في بوت كيمياء السادس العلمي",
        reply_markup=reply_markup
    )

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()
