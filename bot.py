import json
import os
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "8837253510:AAGouArdSY6JhF64AHQuV5P1ajz93w6zLVU"

LOG_GROUP_ID = -1001234567890

OWNER_PASSWORD = "Mrx.106529"
ADMIN_PASSWORD = "106529"

DB_FILE = "data.json"

# ───────── دیتابیس ─────────
def load():
    if not os.path.exists(DB_FILE):
        return {
            "links": {},
            "used": {},
            "vip": [],
            "banned": [],
            "admins": [],
            "logs": {}
        }
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save():
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

db = load()

# ───────── ابزارها ─────────
def gen_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

async def log(app, text):
    db["logs"].setdefault("all", []).append(text)
    save()
    try:
        await app.bot.send_message(LOG_GROUP_ID, text)
    except:
        pass

# ───────── START ─────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)

    if uid in db["banned"]:
        await update.message.reply_text("⛔ شما بن هستید")
        return

    args = context.args

    # ساخت لینک
    if not args:
        code = gen_code()
        db["links"][code] = uid
        save()

        link = f"https://t.me/YourBot?start={code}"
        await update.message.reply_text(f"🔗 لینک اختصاصی تو:\n{link}")

        await log(context.application, f"LINK CREATED {uid} -> {code}")
        return

    code = args[0]

    if code not in db["links"]:
        await update.message.reply_text("❌ لینک نامعتبر")
        return

    db["used"][code] = uid
    save()

    await update.message.reply_text("✅ ورود موفق")

    await log(context.application, f"USER ENTER {uid} WITH {code}")

# ───────── پنل ─────────
def panel_ui():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 کاربران", callback_data="users")],
        [InlineKeyboardButton("🔗 لینک‌ها", callback_data="links")],
        [InlineKeyboardButton("💎 VIP", callback_data="vip")],
        [InlineKeyboardButton("🚫 بن‌ها", callback_data="banned")],
    ])

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎛 پنل مدیریت:", reply_markup=panel_ui())

# ───────── VIP ─────────
async def addvip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return

    uid = context.args[0]

    if uid not in db["vip"]:
        db["vip"].append(uid)
        save()

    await update.message.reply_text("💎 VIP شد")

# ───────── BAN / UNBAN ─────────
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return

    uid = context.args[0]
    db["banned"].append(uid)
    save()

    await update.message.reply_text("🚫 بن شد")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return

    uid = context.args[0]

    if uid in db["banned"]:
        db["banned"].remove(uid)
        save()

    await update.message.reply_text("✅ آنبن شد")

# ───────── دکمه‌ها ─────────
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "users":
        txt = "👥 کاربران:\n\n"
        for k in list(db["links"].values())[:15]:
            txt += f"- {k}\n"
        await q.edit_message_text(txt, reply_markup=panel_ui())

    elif q.data == "links":
        txt = "🔗 لینک‌ها:\n\n"
        for c, u in list(db["links"].items())[:10]:
            status = "❌ استفاده شده" if c in db["used"] else "🟢 فعال"
            txt += f"{c} | {status}\n"
        await q.edit_message_text(txt, reply_markup=panel_ui())

    elif q.data == "vip":
        txt = "💎 VIP ها:\n\n" + "\n".join(db["vip"])
        await q.edit_message_text(txt, reply_markup=panel_ui())

    elif q.data == "banned":
        txt = "🚫 بن‌ها:\n\n" + "\n".join(db["banned"])
        await q.edit_message_text(txt, reply_markup=panel_ui())

# ───────── پیام رمزها ─────────
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    uid = str(update.effective_user.id)

    if msg == OWNER_PASSWORD:
        await update.message.reply_text("👑 مالک وارد شد")
        await log(context.application, f"OWNER LOGIN {uid}")
        return

    if msg == ADMIN_PASSWORD:
        if uid not in db["admins"]:
            db["admins"].append(uid)
            save()

        await update.message.reply_text("🛡 ادمین وارد شد")
        await log(context.application, f"ADMIN LOGIN {uid}")
        return

# ───────── اجرا ─────────
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("panel", panel))
app.add_handler(CommandHandler("addvip", addvip))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))

app.run_polling()
