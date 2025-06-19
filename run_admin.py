#!/usr/bin/env python3
"""
Flask admin panelni ishga tushirish
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from admin.app import app, create_default_admin
from bot.config import Config

if __name__ == "__main__":
    # Konfiguratsiyani tekshirish
    if not Config.SECRET_KEY or Config.SECRET_KEY == 'your-secret-key-here':
        print("⚠️  Ogohlantirish: SECRET_KEY xavfsiz emas!")
        print("ℹ️  .env faylida yangi SECRET_KEY yarating")

    # Kerakli papkalarni yaratish
    Config.init_app()

    # Default admin yaratish
    create_default_admin()

    # Admin panel ma'lumotlarini ko'rsatish
    print("🔐 Flask Admin Panel ishga tushmoqda...")
    print(f"👤 Admin username: {Config.ADMIN_USERNAME}")
    print(f"🔑 Admin password: {Config.ADMIN_PASSWORD}")
    print("-" * 50)
    print("🌐 Admin panel: http://localhost:5000")
    print("ℹ️  Ctrl+C bosib to'xtatish mumkin")
    print("-" * 50)

    try:
        # Development mode
        if Config.FLASK_ENV == 'development':
            app.run(debug=True, host='0.0.0.0', port=5000)
        else:
            # Production mode
            app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n⏹️  Admin panel to'xtatildi")
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        sys.exit(1)