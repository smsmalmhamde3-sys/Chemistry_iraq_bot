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
user_time = {}  # تخزين التايم

# ================= MENU =================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 حلول واجبات", callback_data="hw")],
        [InlineKeyboardButton("📊 درجتي", callback_data="grade")],
        [InlineKeyboardButton("❓ اسأل الأستاذ", callback_data="ask")],
        [InlineKeyboardButton("📢 تنبيهات", callback_data="notify")],
        [InlineKeyboardButton("🗓 موعد الامتحان", callback_data="exam")],
        [InlineKeyboardButton("⏰ اختيار التايم", callback_data="time")],
        [InlineKeyboardButton("🏠 الرئيسية", callback_data="home")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👨‍🏫 مرحباً بك\n"
        "معك الأستاذ حسان 👋\n"
        "📘 مادة الكيمياء\n\n"
        "اختر التايم أولاً ⏰ ثم استخدم القائمة:",
        reply_markup=main_menu()
    )

# ================= CALLBACK =================
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # 🏠 الرئيسية
    if query.data == "home":
        await query.edit_message_text("🏠 القائمة الرئيسية", reply_markup=main_menu())

    # ⏰ اختيار التايم
    elif query.data == "time":
        keyboard = [
            [InlineKeyboardButton("ماسيه 1", callback_data="t1")],
            [InlineKeyboardButton("ماسيه 2", callback_data="t2")],
            [InlineKeyboardButton("ماسيه 3", callback_data="t3")],
            [InlineKeyboardButton("تايم معهد 4", callback_data="t4")],
            [InlineKeyboardButton("تايم معهد 5", callback_data="t5")],
            [InlineKeyboardButton("🏠 رجوع", callback_data="home")]
        ]
        await query.edit_message_text("⏰ اختر التايم:", reply_markup=InlineKeyboardMarkup(keyboard))

    # حفظ التايم
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
            f"✅ تم اختيار التايم: {times[query.data]}",
            reply_markup=main_menu()
        )

    # 📚 واجبات
    elif query.data == "hw":
        keyboard = [
            [InlineKeyboardButton("فصل 1", callback_data="f1")],
            [InlineKeyboardButton("فصل 2", callback_data="f2")],
            [InlineKeyboardButton("فصل 3", callback_data="f3")],
            [InlineKeyboardButton("فصل 4", callback_data="f4")],
            [InlineKeyboardButton("فصل 5", callback_data="f5")],
            [InlineKeyboardButton("فصل 6", callback_data="f6")],
            [InlineKeyboardButton("فصل 7", callback_data="f7")],
            [InlineKeyboardButton("فصل 8", callback_data="f8")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="home")]
        ]
        await query.edit_message_text("📚 اختر الفصل:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("f"):
        await query.edit_message_text("📂 لا توجد واجبات حالياً", reply_markup=main_menu())

    # 📊 درجة
    elif query.data == "grade":
        time = user_time.get(user_id, "غير محدد")

        await context.bot.send_message(
            ADMIN_ID,
            f"📌 طلب درجة\n👤 {users.get(user_id,'غير مسجل')}\n⏰ {time}\n🆔 {user_id}"
        )

        await query.edit_message_text("📊 تم إرسال طلبك", reply_markup=main_menu())

    # ❓ سؤال
    elif query.data == "ask":
        context.user_data["waiting_question"] = True
        await query.edit_message_text("✍️ اكتب سؤالك الآن", reply_markup=main_menu())

    # 📢 تنبيهات
    elif query.data == "notify":
        await query.edit_message_text("📢 لا توجد تنبيهات", reply_markup=main_menu())

    # 🗓 امتحان
    elif query.data == "exam":
        await query.edit_message_text("🗓 موعد الامتحان لاحقاً", reply_markup=main_menu())

    # ✍️ رد على الطالب
    elif query.data.startswith("reply_"):
        target_id = int(query.data.split("_")[1])
        context.user_data["reply_to"] = target_id
        await query.message.reply_text("✍️ اكتب الرد الآن فقط")

# ================= TEXT HANDLER =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id
    text = update.message.text

    # سؤال الطالب
    if context.user_data.get("waiting_question"):
        context.user_data["waiting_question"] = False

        await context.bot.send_message(
            ADMIN_ID,
            f"❓ سؤال جديد\n\n👤 {text}\n🆔 {user_id}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✍️ رد على الطالب", callback_data=f"reply_{user_id}")]
            ])
        )

        await update.message.reply_text("✅ تم إرسال سؤالك")
        return

    # رد الأستاذ
    if context.user_data.get("reply_to"):
        target_id = context.user_data["reply_to"]
        context.user_data["reply_to"] = None

        await context.bot.send_message(
            target_id,
            f"👨‍🏫 رد الأستاذ:\n\n{text}"
        )

        await update.message.reply_text("✅ تم إرسال الرد")
        return

    users[user_id] = text
    await update.message.reply_text("🏠 استخدم القائمة 👇", reply_markup=main_menu())

# ================= RUN =================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

app.run_polling()
