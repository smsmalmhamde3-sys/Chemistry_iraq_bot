import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("8976857022:AAETcfdp17e4n__Bo59HZvx6TEnyMu66k0c")
ADMIN_ID =  int(os.getenv("826754351"))

users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 حلول واجبات", callback_data="hw")],
        [InlineKeyboardButton("❓ اسأل الأستاذ", callback_data="ask")],
        [InlineKeyboardButton("📊 درجتي", callback_data="grade")],
        [InlineKeyboardButton("📢 تنبيهات", callback_data="notify")],
        [InlineKeyboardButton("🗓 موعد الامتحان", callback_data="exam")]
    ]

    await update.message.reply_text(
        "أهلاً 👋 اختر الخدمة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# تسجيل الاسم + التايم
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users[user_id] = update.message.text
    await update.message.reply_text("تم استلام اسمك 👍")

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "grade":
        user = query.from_user
        await context.bot.send_message(
            ADMIN_ID,
            f"📌 طلب درجة\nالاسم: {users.get(user.id,'غير مسجل')}\nID: {user.id}"
        )
        await query.edit_message_text("تم إرسال طلبك للأستاذ 📩")

    elif query.data == "ask":
        await query.edit_message_text("اكتب سؤالك الآن وارسله ✍️")

    elif query.data == "hw":
        await query.edit_message_text("📚 اختار الفصل 1 - 8")

    elif query.data == "notify":
        await query.edit_message_text("📢 تابع التنبيهات من الأستاذ")

    elif query.data == "exam":
        await query.edit_message_text("🗓 موعد الامتحان سيتم إرساله قريباً")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.add_handler(CallbackQueryHandler(callback))

app.run_polling()
