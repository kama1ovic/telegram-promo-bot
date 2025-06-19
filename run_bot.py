#!/usr/bin/env python3
"""
Telegram botni ishga tushirish
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.bot import PromoBot
from bot.config import Config

if __name__ == "__main__":
    # Konfiguratsiyani tekshirish
    if not Config.BOT_TOKEN:
        print("❌ BOT_TOKEN .env faylida ko'rsatilmagan!")
        print("ℹ️  .env faylini yarating va BOT_TOKEN=your_bot_token_here qo'shing")
        sys.exit(1)

    # Kerakli papkalarni yaratish
    Config.init_app()

    # Botni ishga tushirish
    print("🤖 Telegram bot ishga tushmoqda...")
    print(f"📢 Kanal: {Config.CHANNEL_ID}")
    print(f"👤 Admin ID: {Config.ADMIN_TELEGRAM_ID}")
    print("-" * 50)

    try:
        bot = PromoBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n⏹️  Bot to'xtatildi")
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        sys.exit(1)