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
user_time = {}
user_registered = {}
waiting_question = {}

# ================= MENU =================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 حلول واجبات", callback_data="hw")],
        [InlineKeyboardButton("📊 درجتي", callback_data="grade")],
        [InlineKeyboardButton("❓ اسأل الأستاذ", callback_data="ask")],
        [InlineKeyboardButton("📢 تنبيهات", callback_data="notify")],
        [InlineKeyboardButton("🗓 موعد الامتحان", callback_data="exam")],
        [InlineKeyboardButton("🏠 الرئيسية", callback_data="home")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("⏰ اختيار التايم", callback_data="time")]
    ]

    await update.message.reply_text(
        "👨‍🏫 مرحباً بك\n"
        "معك الأستاذ حسان 👋\n"
        "📘 مادة الكيمياء\n\n"
        "ابدأ باختيار التايم ⏰",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= CALLBACK =================
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # ⏰ اختيار التايم
    if query.data == "time":
        keyboard = [
            [InlineKeyboardButton("ماسيه 1", callback_data="t1")],
            [InlineKeyboardButton("ماسيه 2", callback_data="t2")],
            [InlineKeyboardButton("ماسيه 3", callback_data="t3")],
            [InlineKeyboardButton("تايم معهد 4", callback_data="t4")],
            [InlineKeyboardButton("تايم معهد 5", callback_data="t5")]
        ]

        await query.edit_message_text(
            "⏰ اختر التايم:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # حفظ التايم ثم طلب الاسم
    elif query.data in ["t1", "t2", "t3", "t4", "t5"]:

        times = {
            "t1": "ماسيه 1",
            "t2": "ماسيه 2",
            "t3": "ماسيه 3",
            "t4": "تايم معهد 4",
            "t5": "تايم معهد 5"
        }

        user_time[user_id] = times[query.data]

        await query.edit_message_text(
            f"✅ تم اختيار التايم: {times[query.data]}\n\n✍️ الآن اكتب اسمك الثلاثي"
        )

    # 🏠 الرئيسية (تظهر فقط بعد التسجيل)
    elif query.data == "home":

        if not user_registered.get(user_id):
            await query.edit_message_text("⚠️ أكمل التسجيل أولاً")
            return

        await query.edit_message_text(
            "🏠 القائمة الرئيسية",
            reply_markup=main_menu()
        )

    # 📚 واجبات
    elif query.data == "hw":
        await query.edit_message_text("📚 اختر الفصل من 1 إلى 8", reply_markup=main_menu())

    # 📊 درجة
    elif query.data == "grade":

        if not user_registered.get(user_id):
            await query.edit_message_text("⚠️ أكمل التسجيل أولاً")
            return

        await context.bot.send_message(
            ADMIN_ID,
            f"📌 طلب درجة\n"
            f"👤 {users.get(user_id)}\n"
            f"⏰ {user_time.get(user_id)}\n"
            f"🆔 {user_id}"
        )

        await query.edit_message_text("📊 تم إرسال طلبك")

    # ❓ سؤال
    elif query.data == "ask":

        if not user_registered.get(user_id):
            await query.edit_message_text("⚠️ أكمل التسجيل أولاً")
            return

        waiting_question[user_id] = True
        await query.edit_message_text("✍️ اكتب سؤالك الآن")

    # 📢 تنبيهات
    elif query.data == "notify":
        await query.edit_message_text("📢 لا توجد تنبيهات")

    # 🗓 امتحان
    elif query.data == "exam":
        await query.edit_message_text("🗓 موعد الامتحان لاحقاً")

    # ✍️ رد الأستاذ
    elif query.data.startswith("reply_"):

        target_id = int(query.data.split("_")[1])
        context.user_data["reply_to"] = target_id

        await query.message.reply_text("✍️ اكتب الرد الآن فقط")

# ================= TEXT HANDLER =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id
    text = update.message.text

    # 1️⃣ تسجيل الاسم بعد التايم
    if user_id in user_time and not user_registered.get(user_id):
        users[user_id] = text
        user_registered[user_id] = True

        await update.message.reply_text(
            "✅ تم تسجيلك بنجاح",
            reply_markup=main_menu()
        )
        return

    # 2️⃣ سؤال الطالب
    if waiting_question.get(user_id):
        waiting_question[user_id] = False

        await context.bot.send_message(
            ADMIN_ID,
            f"❓ سؤال جديد\n\n"
            f"👤 الاسم: {users.get(user_id)}\n"
            f"⏰ التايم: {user_time.get(user_id)}\n"
            f"🆔 ID: {user_id}\n\n"
            f"📝 السؤال: {text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✍️ رد على الطالب", callback_data=f"reply_{user_id}")]
            ])
        )

        await update.message.reply_text("✅ تم إرسال سؤالك")
        return

    # 3️⃣ رد الأستاذ
    if context.user_data.get("reply_to"):
        target_id = context.user_data["reply_to"]
        context.user_data["reply_to"] = None

        await context.bot.send_message(
            target_id,
            f"👨‍🏫 رد الأستاذ:\n\n{text}"
        )

        await update.message.reply_text("✅ تم إرسال الرد")
        return

# ================= RUN =================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

app.run_polling()
