import logging
import sqlite3
import json
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ========== تنظیمات ==========
TOKEN = "8415084076:AAFUuWgyOGXK3aFv5zp9ILwMRKSdcV8TtYI"
ADMIN_ID = 7744236569
XRAY_URL = "https://your-xray.onrender.com"

# ========== دیتابیس ==========
def init_db():
    conn = sqlite3.connect("vpn_bot.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        role TEXT DEFAULT 'user',
        wallet INTEGER DEFAULT 0,
        uuid TEXT,
        expire_date TEXT,
        used_traffic INTEGER DEFAULT 0,
        config_link TEXT
    )''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("vpn_bot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return {
            "user_id": user[0],
            "role": user[1],
            "wallet": user[2],
            "uuid": user[3],
            "expire_date": user[4],
            "used_traffic": user[5],
            "config_link": user[6]
        }
    return None

def add_user(user_id, role='user', wallet=0):
    conn = sqlite3.connect("vpn_bot.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, role, wallet) VALUES (?, ?, ?)", (user_id, role, wallet))
    conn.commit()
    conn.close()

def update_wallet(user_id, amount):
    conn = sqlite3.connect("vpn_bot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET wallet = wallet + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def set_config(user_id, uuid, expire_date, config_link):
    conn = sqlite3.connect("vpn_bot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET uuid = ?, expire_date = ?, config_link = ? WHERE user_id = ?", (uuid, expire_date, config_link, user_id))
    conn.commit()
    conn.close()

# ========== دکمه‌ها ==========
def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛒 خرید کانفیگ", callback_data="buy")],
        [InlineKeyboardButton("💰 کیف پول", callback_data="wallet")],
        [InlineKeyboardButton("📊 وضعیت کانفیگ", callback_data="status")],
        [InlineKeyboardButton("👤 پروفایل", callback_data="profile")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== شروع ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    
    try:
        await update.message.reply_sticker("CAACAgQAAxkBAAEBAA")
    except:
        pass
    
    text = (
        "سلام کیری\n"
        "به کصکش ترین ربات فیلتر شکن فروشی خوش آمدید"
    )
    await update.message.reply_text(text, reply_markup=main_keyboard())

# ========== خرید کانفیگ ==========
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = get_user(user_id)
    
    if not user:
        await query.edit_message_text("❌ ثبت‌نام نکردی کیری!")
        return
    
    text = (
        "گیگ: ۱۰ گیگ\n"
        "چند روزه: ۳۰ روزه\n"
        "تاریخ انقضا: ۳۰ روز بعد\n"
        "مبلغ: ۵۰,۰۰۰ تومان\n\n"
        "اگر می‌خوای بخری انگشت کیری‌ات رو روی دکمه زیر لمس کن"
    )
    keyboard = [[InlineKeyboardButton("خرید کانفیگ", callback_data="confirm_buy")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def confirm_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = get_user(user_id)
    
    if user['wallet'] < 50000:
        await query.edit_message_text("بیااااااااا🖕\nبرو کیف پولت رو شارژ کن کصکش")
        return
    
    uuid = "test-uuid-123"
    expire = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    config_link = "vless://test@example.com:443"
    
    update_wallet(user_id, -50000)
    set_config(user_id, uuid, expire, config_link)
    
    await query.edit_message_text(
        f"✅ کانفیگ خریداری شد!\n\n"
        f"گیگ: ۱۰ گیگ\n"
        f"چند روزه: ۳۰ روزه\n"
        f"تاریخ انقضا: {expire}\n"
        f"مبلغ پرداختی: ۵۰,۰۰۰ تومان\n\n"
        f"لینک کانفیگ:\n{config_link}"
    )

# ========== کیف پول ==========
async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = get_user(user_id)
    
    if not user:
        await query.edit_message_text("❌ ثبت‌نام نکردی کیری!")
        return
    
    if user['wallet'] <= 0:
        wallet_text = "🖕"
    else:
        wallet_text = f"{user['wallet']:,} تومان"
    
    text = f"حساب: {user_id}\nموجودی کیف پول: {wallet_text}"
    keyboard = [[InlineKeyboardButton("شارژ کیف پول", callback_data="charge")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def charge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        "شماره کارت\n"
        "6219861439976183\n"
        "کریم جاهدی\n\n"
        "عکس رسید بفرست"
    )
    await query.edit_message_text(text)

# ========== مدیریت رسید ==========
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = f"یک کیری آیدی {user_id} واست پول زده قبول میکنی یا نه"
    keyboard = [
        [
            InlineKeyboardButton("آره", callback_data=f"accept_{user_id}"),
            InlineKeyboardButton("نه", callback_data=f"reject_{user_id}")
        ]
    ]
    await context.bot.send_message(ADMIN_ID, text, reply_markup=InlineKeyboardMarkup(keyboard))
    await update.message.reply_text("واستا کیری\nادمین ها باید قبول کنن")

async def accept_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split("_")[1])
    update_wallet(user_id, 50000)
    await query.edit_message_text(f"✅ کیف پول کاربر {user_id} شارژ شد کیری")
    await context.bot.send_message(user_id, "✅ کیف پولت شارژ شد کیری")

async def reject_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split("_")[1])
    await query.edit_message_text(f"❌ رد شدی کصکش، برو گریه کن")
    await context.bot.send_message(user_id, "❌ رد شدی کصکش، برو گریه کن")

# ========== وضعیت کانفیگ ==========
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = get_user(user_id)
    
    if not user or not user['uuid']:
        await query.edit_message_text("❌ کانفیگ فعالی نداری کیری\nبرو یه کانفیگ بخر")
        return
    
    if user['expire_date']:
        expire = datetime.strptime(user['expire_date'], "%Y-%m-%d")
        days_left = (expire - datetime.now()).days
        if days_left < 0:
            days_left = 0
    else:
        days_left = 0
    
    text = (
        f"مقدار کانفیگ خریدی: ۱۰ گیگ\n"
        f"چند روز مانده: {days_left} روز\n"
        f"مقدار سوپر دانلود شده: {user['used_traffic']} گیگ"
    )
    await query.edit_message_text(text)

# ========== پروفایل ==========
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = get_user(user_id)
    
    if not user:
        await query.edit_message_text("❌ ثبت‌نام نکردی کیری!")
        return
    
    text = (
        f"👤 پروفایل\n"
        f"آیدی: {user_id}\n"
        f"نقش: {'👑 ادمین' if user['role'] == 'admin' else 'کاربر عادی'}\n"
        f"موجودی: {user['wallet']:,} تومان\n"
        f"وضعیت: {'✅ فعال' if user['uuid'] else '❌ بدون کانفیگ'}"
    )
    await query.edit_message_text(text)

# ========== اصلی ==========
def main():
    init_db()
    
    admin = get_user(ADMIN_ID)
    if not admin:
        add_user(ADMIN_ID, 'admin', 100000000000)
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buy, pattern="^buy$"))
    app.add_handler(CallbackQueryHandler(confirm_buy, pattern="^confirm_buy$"))
    app.add_handler(CallbackQueryHandler(wallet, pattern="^wallet$"))
    app.add_handler(CallbackQueryHandler(charge, pattern="^charge$"))
    app.add_handler(CallbackQueryHandler(accept_payment, pattern="^accept_"))
    app.add_handler(CallbackQueryHandler(reject_payment, pattern="^reject_"))
    app.add_handler(CallbackQueryHandler(status, pattern="^status$"))
    app.add_handler(CallbackQueryHandler(profile, pattern="^profile$"))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("ربات روشن شد ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
