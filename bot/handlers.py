"""
Bot uchun yordamchi handlerlar
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class Handlers:
    def __init__(self, database, config):
        self.db = database
        self.config = config

    async def back_to_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Menuga qaytish"""
        query = update.callback_query
        await query.answer()

        language = context.user_data.get('language', 'uz')

        texts = {
            'uz': "📝 Iltimos, 8 xonali kodni kiriting:",
            'ru': "📝 Пожалуйста, введите 8-значный код:"
        }

        keyboard = [
            [InlineKeyboardButton("📊 Statistika", callback_data="statistics")],
            [InlineKeyboardButton("🔙 Bosh menu", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            texts[language],
            reply_markup=reply_markup
        )

    async def enter_new_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Yangi kod kiritish"""
        query = update.callback_query
        await query.answer()

        language = context.user_data.get('language', 'uz')

        texts = {
            'uz': "📝 Iltimos, yangi 8 xonali kodni kiriting:",
            'ru': "📝 Пожалуйста, введите новый 8-значный код:"
        }

        keyboard = [
            [InlineKeyboardButton("📊 Statistika", callback_data="statistics")],
            [InlineKeyboardButton("🔙 Bosh menu", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            texts[language],
            reply_markup=reply_markup
        )

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xatoliklarni qayta ishlash"""
        logger.error(f"Update {update} caused error {context.error}")

        if update and update.effective_message:
            language = context.user_data.get('language', 'uz')

            texts = {
                'uz': "❌ Xatolik yuz berdi. Qaytadan /start buyrug'ini yuboring.",
                'ru': "❌ Произошла ошибка. Отправьте команду /start снова."
            }

            try:
                await update.effective_message.reply_text(texts[language])
            except:
                pass