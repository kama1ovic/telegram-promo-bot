"""
Bot konfiguratsiya fayli
"""

import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()


class Config:
    # Telegram Bot
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    CHANNEL_ID = os.getenv('CHANNEL_ID', '@test_channel')
    CHANNEL_CHAT_ID = int(os.getenv('CHANNEL_CHAT_ID', '-1001234567890'))
    ADMIN_TELEGRAM_ID = int(os.getenv('ADMIN_TELEGRAM_ID', '123456789'))

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///promo_bot.db')

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # Admin
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

    # Upload folder
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip'}

    @staticmethod
    def init_app():
        """Kerakli papkalarni yaratish"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)