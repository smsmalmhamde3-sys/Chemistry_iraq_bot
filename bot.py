import os
import sqlite3
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

# ================= DATABASE =================
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    time TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS grades (
    user_id INTEGER,
    subject TEXT,
    grade TEXT
)
""")

conn.commit()

def save_user(user_id, name=None, time=None):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone():
        if name:
            cursor.execute("UPDATE users SET name=? WHERE user_id=?", (name, user_id))
        if time:
            cursor.execute("UPDATE users SET time=? WHERE user_id=?", (time, user_id))
    else:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (user_id, name, time))
    conn.commit()

def get_user(user_id):
    cursor.execute("SELECT name, time FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def add_grade(user_id, subject, grade):
    cursor.execute("INSERT INTO grades VALUES (?, ?, ?)", (user_id, subject, grade))
    conn.commit()

# ================= STATE =================
waiting_name = {}
waiting_question = {}
admin_step = {}

# ================= MENU =================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 واجبات", callback_data="hw")],
        [InlineKeyboardButton("📊 درجتي", callback_data="grade")],
        [InlineKeyboardButton("❓ اسأل الأستاذ", callback_data="ask")],
        [InlineKeyboardButton("📢 تنبيهات", callback_data="notify")],
        [InlineKeyboardButton("🗓 امتحان", callback_data="exam")],
        [InlineKeyboardButton("👩‍🏫 لوحة الأستاذ", callback_data="admin")],
        [InlineKeyboardButton("🏠 الرئيسية", callback_data="home")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("⏰ اختيار التايم", callback_data="time")]
    ]

    await update.message.reply_text(
        "👨‍🏫 مرحباً بك\n"
        "مادة الكيمياء\n\n"
        "ابدأ باختيار التايم ⏰",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= CALLBACK =================
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # ⏰ التايم
    if query.data == "time":
        keyboard = [
            [InlineKeyboardButton("ماسيه 1", callback_data="t1")],
            [InlineKeyboardButton("ماسيه 2", callback_data="t2")],
            [InlineKeyboardButton("ماسيه 3", callback_data="t3")],
            [InlineKeyboardButton("تايم معهد 4", callback_data="t4")],
            [InlineKeyboardButton("تايم معهد 5", callback_data="t5")]
        ]
        await query.edit_message_text("⏰ اختر التايم:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data in ["t1","t2","t3","t4","t5"]:

        times = {
            "t1":"ماسيه 1",
            "t2":"ماسيه 2",
            "t3":"ماسيه 3",
            "t4":"تايم معهد 4",
            "t5":"تايم معهد 5"
        }

        save_user(user_id, time=times[query.data])
        waiting_name[user_id] = True

        await query.edit_message_text("✍️ اكتب اسمك الثلاثي")

    # 🏠 الرئيسية
    elif query.data == "home":
        await query.edit_message_text("🏠 القائمة", reply_markup=main_menu())

    # 📚 واجبات
    elif query.data == "hw":
        keyboard = [
            [InlineKeyboardButton(f"فصل {i}", callback_data=f"f{i}")] for i in range(1,9)
        ]
        keyboard.append([InlineKeyboardButton("🏠 الرئيسية", callback_data="home")])

        await query.edit_message_text("📚 اختر الفصل", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("f"):
        await query.edit_message_text("📂 لا توجد واجبات")

    # 📊 درجة
    elif query.data == "grade":
        u = get_user(user_id)
        if not u:
            await query.edit_message_text("⚠️ سجل أولاً")
            return

        await context.bot.send_message(
            ADMIN_ID,
            f"📊 طلب درجة\n👤 {u[0]}\n⏰ {u[1]}\n🆔 {user_id}"
        )
        await query.edit_message_text("📊 تم الإرسال")

    # ❓ سؤال
    elif query.data == "ask":
        waiting_question[user_id] = True
        await query.edit_message_text("✍️ اكتب سؤالك")

    # 👩‍🏫 لوحة الأستاذ
    elif query.data == "admin":
        if user_id != ADMIN_ID:
            return

        keyboard = [
            [InlineKeyboardButton("📊 إضافة درجة", callback_data="add_grade")],
            [InlineKeyboardButton("📢 إعلان", callback_data="broadcast")],
            [InlineKeyboardButton("📋 الطلاب", callback_data="students")]
        ]
        await query.edit_message_text("👩‍🏫 لوحة الأستاذ", reply_markup=InlineKeyboardMarkup(keyboard))

    # ✍️ رد
    elif query.data.startswith("reply_"):
        target = int(query.data.split("_")[1])
        context.user_data["reply_to"] = target
        await query.message.reply_text("✍️ اكتب الرد")

# ================= TEXT =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id
    text = update.message.text

    # 👤 تسجيل الاسم
    if waiting_name.get(user_id):
        waiting_name[user_id] = False
        save_user(user_id, name=text)
        await update.message.reply_text("✅ تم التسجيل", reply_markup=main_menu())
        return

    # ❓ سؤال
    if waiting_question.get(user_id):
        waiting_question[user_id] = False

        u = get_user(user_id)

        await context.bot.send_message(
            ADMIN_ID,
            f"❓ سؤال\n👤 {u[0]}\n⏰ {u[1]}\n🆔 {user_id}\n\n📝 {text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✍️ رد", callback_data=f"reply_{user_id}")]
            ])
        )

        await update.message.reply_text("✅ تم الإرسال")
        return

    # 👨‍🏫 رد الأستاذ
    if context.user_data.get("reply_to"):
        target = context.user_data["reply_to"]
        context.user_data["reply_to"] = None

        await context.bot.send_message(target, f"👨‍🏫 رد الأستاذ:\n\n{text}")
        await update.message.reply_text("✅ تم الرد")
        return

# ================= RUN =================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

app.run_polling()
