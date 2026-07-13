import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
import json

# تنظیمات
BOT_TOKEN = "8793482183:AAEGUa7ZEURP26N34DzKvrudnndC3q7apBk"
PANEL_URL = "http://localhost:5000"
ADMIN_PASSWORD = "admin123"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 آمار", callback_data="stats")],
        [InlineKeyboardButton("👥 کاربران", callback_data="users")],
        [InlineKeyboardButton("➕ افزودن کاربر", callback_data="add_user")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 **پنل X-Panel**\nبه بات مدیریت خوش آمدید!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # درخواست به پنل
        response = requests.get(f"{PANEL_URL}/api/stats")
        stats = response.json()
        
        text = f"📊 **آمار پنل**\n\n"
        text += f"👥 کاربران کل: {stats['total_users']}\n"
        text += f"✅ کاربران فعال: {stats['active_users']}\n"
        text += f"📦 ترافیک کل: {stats['total_traffic'] / (1024**3):.2f} GB"
        
        await update.callback_query.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        await update.callback_query.message.reply_text(f"❌ خطا: {str(e)}")

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(f"{PANEL_URL}/api/users")
        users = response.json()
        
        if not users:
            await update.callback_query.message.reply_text("📭 هیچ کاربری یافت نشد")
            return
        
        text = "👥 **لیست کاربران:**\n\n"
        for user in users[:10]:
            used = user['traffic_used'] / (1024**3)
            limit = user['traffic_limit'] / (1024**3)
            text += f"• {user['name']}: {used:.1f}/{limit:.0f} GB ({user['status']})\n"
        
        await update.callback_query.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        await update.callback_query.message.reply_text(f"❌ خطا: {str(e)}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "stats":
        await stats(update, context)
    elif query.data == "users":
        await users(update, context)
    elif query.data == "add_user":
        await query.message.reply_text(
            "➕ **افزودن کاربر جدید**\n\n"
            "فرمت:\n"
            "/add [نام] [ترافیک_GB] [روز]\n\n"
            "مثال:\n"
            "/add علی 10 30"
        )

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("⚠️ فرمت: /add [نام] [ترافیک_GB] [روز]")
            return
        
        name = args[0]
        traffic = int(args[1])
        days = int(args[2])
        
        # ارسال به پنل
        data = {
            "name": name,
            "traffic_limit": traffic,
            "expiry_days": days
        }
        response = requests.post(f"{PANEL_URL}/api/users", json=data)
        
        if response.status_code == 200:
            await update.message.reply_text(f"✅ کاربر {name} با موفقیت افزوده شد!")
        else:
            await update.message.reply_text(f"❌ خطا: {response.text}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")

def main():
    # ایجاد اپلیکیشن
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ثبت دستورات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_user))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # اجرا
    print("🤖 بات در حال اجراست...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
