import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json

# تنظیمات
BOT_TOKEN = "8793482183:AAEGUa7ZEURP26N34DzKvrudnndC3q7apBk"
PANEL_URL = "http://localhost:5000"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📊 آمار", callback_data="stats"),
        InlineKeyboardButton("👥 کاربران", callback_data="users"),
        InlineKeyboardButton("➕ افزودن کاربر", callback_data="add_user")
    )
    
    bot.send_message(
        message.chat.id,
        "🤖 **پنل X-Panel**\nبه بات مدیریت خوش آمدید!",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "stats":
        try:
            response = requests.get(f"{PANEL_URL}/api/stats")
            stats = response.json()
            
            text = f"📊 **آمار پنل**\n\n"
            text += f"👥 کاربران کل: {stats.get('total_users', 0)}\n"
            text += f"✅ کاربران فعال: {stats.get('active_users', 0)}\n"
            text += f"📦 ترافیک کل: {stats.get('total_traffic', 0) / (1024**3):.2f} GB"
            
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ خطا: {str(e)}")
    
    elif call.data == "users":
        try:
            response = requests.get(f"{PANEL_URL}/api/users")
            users = response.json()
            
            if not users:
                bot.edit_message_text("📭 هیچ کاربری یافت نشد", call.message.chat.id, call.message.message_id)
                return
            
            text = "👥 **لیست کاربران:**\n\n"
            for user in users[:10]:
                used = user.get('traffic_used', 0) / (1024**3)
                limit = user.get('traffic_limit', 10)
                text += f"• {user.get('name', 'نامشخص')}: {used:.1f}/{limit:.0f} GB ({user.get('status', 'unknown')})\n"
            
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ خطا: {str(e)}")
    
    elif call.data == "add_user":
        bot.edit_message_text(
            "➕ **افزودن کاربر جدید**\n\n"
            "فرمت:\n"
            "/add [نام] [ترافیک_GB] [روز]\n\n"
            "مثال:\n"
            "/add علی 10 30",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )

@bot.message_handler(commands=['add'])
def add_user(message):
    try:
        args = message.text.split()
        if len(args) < 4:
            bot.reply_to(message, "⚠️ فرمت: /add [نام] [ترافیک_GB] [روز]")
            return
        
        name = args[1]
        traffic = int(args[2])
        days = int(args[3])
        
        data = {
            "name": name,
            "traffic_limit": traffic,
            "expiry_days": days
        }
        response = requests.post(f"{PANEL_URL}/api/users", json=data)
        
        if response.status_code == 200:
            bot.reply_to(message, f"✅ کاربر {name} با موفقیت افزوده شد!")
        else:
            bot.reply_to(message, f"❌ خطا: {response.text}")
    except Exception as e:
        bot.reply_to(message, f"❌ خطا: {str(e)}")

@bot.message_handler(commands=['help'])
def help_command(message):
    text = """
📚 **راهنمای بات**

دستورات:
/start - نمایش منو
/add [نام] [ترافیک_GB] [روز] - افزودن کاربر
/help - این راهنما

دکمه‌ها:
📊 آمار - نمایش آمار پنل
👥 کاربران - لیست کاربران
➕ افزودن کاربر - راهنمای افزودن
"""
    bot.reply_to(message, text, parse_mode='Markdown')

if __name__ == "__main__":
    print("🤖 بات در حال اجراست...")
    bot.polling()
