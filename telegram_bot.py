import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json

BOT_TOKEN = "8793482183:AAEGUa7ZEURP26N34DzKvrudnndC3q7apBk"
PANEL_URL = "http://localhost:5000"
ADMIN_IDS = [8680457924]  

bot = telebot.TeleBot(BOT_TOKEN)

def get_panel_token():
    response = requests.post(f"{PANEL_URL}/login", json={"password": "admin123"})
    return response.json().get('token')

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
        "🤖 **پنل X-Panel**\n"
        "به بات مدیریت خوش آمدید!",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    token = get_panel_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    if call.data == "stats":
        response = requests.get(f"{PANEL_URL}/api/stats", headers=headers)
        stats = response.json()
        
        text = f"📊 **آمار پنل**\n\n"
        text += f"👥 کاربران کل: {stats['total_users']}\n"
        text += f"✅ کاربران فعال: {stats['active_users']}\n"
        text += f"📦 ترافیک کل: {stats['total_traffic'] / (1024**3):.2f} GB"
        
        bot.send_message(call.message.chat.id, text, parse_mode='Markdown')
    
    elif call.data == "users":
        response = requests.get(f"{PANEL_URL}/api/users", headers=headers)
        users = response.json()
        
        if not users:
            bot.send_message(call.message.chat.id, "📭 هیچ کاربری یافت نشد")
            return
        
        text = "👥 **لیست کاربران:**\n\n"
        for user in users[:10]:
            used = user['traffic_used'] / (1024**3)
            limit = user['traffic_limit'] / (1024**3)
            text += f"• {user['name']}: {used:.1f}/{limit:.0f} GB ({user['status']})\n"
        
        bot.send_message(call.message.chat.id, text, parse_mode='Markdown')

if __name__ == "__main__":
    print("🤖 بات در حال اجراست...")
    bot.polling()
