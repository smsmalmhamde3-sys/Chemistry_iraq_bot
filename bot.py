import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else 0

users = {}
waiting_question = {}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📚 حلول واجبات", callback_data="hw")],
        [InlineKeyboardButton("📊 درجتي", callback_data="grade")],
        [InlineKeyboardButton("❓ اسأل الأستاذ", callback_data="ask")],
        [InlineKeyboardButton("📢 تنبيهات", callback_data="notify")],
        [InlineKeyboardButton("🗓 موعد الامتحان", callback_data="exam")]
    ]

    await update.message.reply_text(
        "👨‍🏫 مرحباً بك\n"
        "معك الأستاذ حسان 👋\n"
        "📘 مادة الكيمياء\n\n"
        "🧑‍🎓 قبل البدء اختر التايم واكتب اسمك:\n\n"
        "ماسيه 1\nماسيه 2\nماسيه 3\nتايم 4\nتايم 5 (معهد)\n\n"
        "مثال: أحمد - ماسيه 1\n\n"
        "ثم اختر من الأزرار:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= تسجيل الاسم =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    users[user_id] = text

    # سؤال الأستاذ
    if waiting_question.get(user_id):
        waiting_question[user_id] = False

        await context.bot.send_message(
            ADMIN_ID,
            f"❓ سؤال جديد\n\n👤 الطالب: {text}\n🆔 ID: {user_id}"
        )

        await update.message.reply_text("✅ تم إرسال سؤالك للأستاذ")
        return

    await update.message.reply_text("✅ تم تسجيل بياناتك")

# ================= الأزرار =================
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    name = users.get(user_id, "غير مسجل")

    # 📚 واجبات
    if query.data == "hw":
        keyboard = [
            [InlineKeyboardButton("فصل 1", callback_data="f1")],
            [InlineKeyboardButton("فصل 2", callback_data="f2")],
            [InlineKeyboardButton("فصل 3", callback_data="f3")],
            [InlineKeyboardButton("فصل 4", callback_data="f4")],
            [InlineKeyboardButton("فصل 5", callback_data="f5")],
            [InlineKeyboardButton("فصل 6", callback_data="f6")],
            [InlineKeyboardButton("فصل 7", callback_data="f7")],
            [InlineKeyboardButton("فصل 8", callback_data="f8")]
        ]

        await query.edit_message_text(
            "📚 اختر الفصل:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("f"):
        await query.edit_message_text("📂 لا توجد واجبات لهذا الفصل حالياً")

    # 📊 درجة
    elif query.data == "grade":
        if ADMIN_ID:
            await context.bot.send_message(
                ADMIN_ID,
                f"📌 طلب درجة\n\n👤 الطالب: {name}\n🆔 ID: {user_id}"
            )
        await query.edit_message_text("📊 تم إرسال طلب الدرجة للأستاذ")

    # ❓ سؤال الأستاذ
    elif query.data == "ask":
        waiting_question[user_id] = True
        await query.edit_message_text("✍️ اكتب سؤالك الآن وسيتم إرساله للأستاذ")

    # 📢 تنبيهات
    elif query.data == "notify":
        await query.edit_message_text("📢 لا توجد تنبيهات حالياً")

    # 🗓 امتحان
    elif query.data == "exam":
        await query.edit_message_text("🗓 موعد الامتحان سيتم تحديده لاحقاً")

# ================= تشغيل =================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.add_handler(CallbackQueryHandler(callback))

app.run_polling()
