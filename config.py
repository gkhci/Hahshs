import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-key-123456')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    JWT_SECRET = os.getenv('JWT_SECRET', 'jwt-secret-key-789')
    
    # تنظیمات سرور
    SERVER_IP = os.getenv('SERVER_IP', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', 5000))
    
    # تنظیمات Xray
    XRAY_API = os.getenv('XRAY_API', '127.0.0.1:10085')
    XRAY_CONFIG = os.getenv('XRAY_CONFIG', '/etc/xray/config.json')
    
    # تنظیمات بات
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    ADMIN_IDS = os.getenv('ADMIN_IDS', '').split(',')
    
    # تنظیمات دیتابیس
    DB_PATH = 'users.json'
    LOGS_PATH = 'logs/'
