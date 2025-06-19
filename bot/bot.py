#!/usr/bin/env python3
"""
Telegram Promo Bot - Asosiy bot fayli
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
from bot.config import Config
from bot.database import Database
from bot.handlers import Handlers
import asyncio

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
LANGUAGE_SELECTION = 0
CHECK_SUBSCRIPTION = 1
ENTER_CODE = 2


class PromoBot:
    def __init__(self):
        self.config = Config()
        self.db = Database()
        self.handlers = Handlers(self.db, self.config)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start komandasi"""
        user = update.effective_user

        # Foydalanuvchini bazaga qo'shish
        self.db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

        # Til tanlash klaviaturasi
        keyboard = [
            [
                InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
                InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🌐 Tilni tanlang / Выберите язык:",
            reply_markup=reply_markup
        )

        return LANGUAGE_SELECTION

    async def language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Til tanlash"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        language = query.data.split('_')[1]

        # Tilni saqlash
        self.db.update_user_language(user_id, language)
        context.user_data['language'] = language

        # Kanalga obuna bo'lish
        texts = {
            'uz': {
                'subscribe': "📢 Botdan foydalanish uchun kanalimizga obuna bo'ling:",
                'channel': "Kanalga o'tish",
                'check': "✅ Obunani tekshirish"
            },
            'ru': {
                'subscribe': "📢 Для использования бота подпишитесь на наш канал:",
                'channel': "Перейти на канал",
                'check': "✅ Проверить подписку"
            }
        }

        text = texts[language]
        keyboard = [
            [InlineKeyboardButton(text['channel'], url=f"https://t.me/{self.config.CHANNEL_ID[1:]}")],
            [InlineKeyboardButton(text['check'], callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text['subscribe'],
            reply_markup=reply_markup
        )

        return CHECK_SUBSCRIPTION

    async def check_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obuna tekshirish"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        language = context.user_data.get('language', 'uz')

        try:
            # Kanalga obuna bo'lganini tekshirish
            chat_member = await context.bot.get_chat_member(
                chat_id=self.config.CHANNEL_CHAT_ID,
                user_id=user_id
            )

            if chat_member.status in ['member', 'administrator', 'creator']:
                # Obuna bo'lgan
                texts = {
                    'uz': "✅ Obuna tasdiqlandi!\n\n📝 Iltimos, 8 xonali kodni kiriting:",
                    'ru': "✅ Подписка подтверждена!\n\n📝 Пожалуйста, введите 8-значный код:"
                }

                # Menu tugmalarini qo'shish
                keyboard = [
                    [InlineKeyboardButton("📊 Statistika", callback_data="statistics")],
                    [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_start")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(
                    texts[language],
                    reply_markup=reply_markup
                )

                return ENTER_CODE
            else:
                # Obuna bo'lmagan
                texts = {
                    'uz': "❌ Siz hali kanalga obuna bo'lmagansiz!",
                    'ru': "❌ Вы еще не подписались на канал!"
                }
                await query.answer(texts[language], show_alert=True)
                return CHECK_SUBSCRIPTION

        except Exception as e:
            logger.error(f"Subscription check error: {e}")
            texts = {
                'uz': "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.",
                'ru': "❌ Произошла ошибка. Попробуйте снова."
            }
            await query.answer(texts[language], show_alert=True)
            return CHECK_SUBSCRIPTION

    async def handle_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Kod kiritishni qayta ishlash"""
        user_id = update.effective_user.id
        language = context.user_data.get('language', 'uz')
        code = update.message.text.strip()

        # Kod formatini tekshirish (8 xonali)
        if len(code) != 8:
            texts = {
                'uz': "❌ Kod 8 xonali bo'lishi kerak!",
                'ru': "❌ Код должен состоять из 8 символов!"
            }
            await update.message.reply_text(texts[language])
            return ENTER_CODE

        # Kodni bazadan tekshirish
        result = self.db.check_and_use_code(user_id, code)

        if result['status'] == 'already_used':
            texts = {
                'uz': "❌ Bu kod allaqachon ishlatilgan!",
                'ru': "❌ Этот код уже использован!"
            }
            await update.message.reply_text(texts[language])
        elif result['status'] == 'invalid':
            texts = {
                'uz': "❌ Noto'g'ri kod!",
                'ru': "❌ Неверный код!"
            }
            await update.message.reply_text(texts[language])
        elif result['status'] == 'success':
            if result['is_winning']:
                texts = {
                    'uz': "🎉 Tabriklaymiz! Siz yutuqli kod kiritdingiz!",
                    'ru': "🎉 Поздравляем! Вы ввели выигрышный код!"
                }
                # Admin'ga xabar yuborish
                await self.notify_admin_winning_code(context, user_id, code)
            else:
                texts = {
                    'uz': "✅ Kod qabul qilindi, ammo yutuqsiz.",
                    'ru': "✅ Код принят, но без выигрыша."
                }
            await update.message.reply_text(texts[language])

        # Menu tugmalarini ko'rsatish
        keyboard = [
            [InlineKeyboardButton("📝 Yangi kod kiritish", callback_data="enter_new_code")],
            [InlineKeyboardButton("📊 Statistika", callback_data="statistics")],
            [InlineKeyboardButton("🔙 Bosh menu", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        texts = {
            'uz': "Tanlang:",
            'ru': "Выберите:"
        }

        await update.message.reply_text(texts[language], reply_markup=reply_markup)

        return ConversationHandler.END

    async def statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Statistikani ko'rsatish"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        language = context.user_data.get('language', 'uz')

        stats = self.db.get_user_statistics(user_id)

        texts = {
            'uz': f"""📊 Sizning statistikangiz:

✅ Kiritilgan kodlar soni: {stats['total_codes']}
🎯 Yutuqli kodlar: {stats['winning_codes']}
❌ Yutuqsiz kodlar: {stats['losing_codes']}
📅 Birinchi kod: {stats['first_code_date'] or 'Hali kiritilmagan'}
📅 Oxirgi kod: {stats['last_code_date'] or 'Hali kiritilmagan'}""",
            'ru': f"""📊 Ваша статистика:

✅ Введено кодов: {stats['total_codes']}
🎯 Выигрышных кодов: {stats['winning_codes']}
❌ Проигрышных кодов: {stats['losing_codes']}
📅 Первый код: {stats['first_code_date'] or 'Еще не введен'}
📅 Последний код: {stats['last_code_date'] or 'Еще не введен'}"""
        }

        keyboard = [
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            texts[language],
            reply_markup=reply_markup
        )

    async def notify_admin_winning_code(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, code: str):
        """Admin'ga yutuqli kod haqida xabar yuborish"""
        user_info = self.db.get_user_info(user_id)

        message = f"""🎉 YUTUQLI KOD KIRITILDI!

👤 Foydalanuvchi: {user_info['first_name']} {user_info['last_name'] or ''}
🆔 Username: @{user_info['username'] or 'username_yoq'}
🆔 User ID: {user_id}
📱 Telefon: {user_info['phone_number'] or 'Kiritilmagan'}
🎫 Kod: {code}
📅 Vaqt: {user_info['created_at']}"""

        try:
            await context.bot.send_message(
                chat_id=self.config.ADMIN_TELEGRAM_ID,
                text=message
            )
        except Exception as e:
            logger.error(f"Admin notification error: {e}")

    async def broadcast_message(self, message_data: dict):
        """Hammaga xabar yuborish (admin panel uchun)"""
        users = self.db.get_all_users()
        success_count = 0

        for user in users:
            try:
                # Text xabar
                if message_data.get('text'):
                    await self.app.bot.send_message(
                        chat_id=user['user_id'],
                        text=message_data['text']
                    )

                # Fayl yuborish
                if message_data.get('file_path'):
                    with open(message_data['file_path'], 'rb') as file:
                        await self.app.bot.send_document(
                            chat_id=user['user_id'],
                            document=file,
                            caption=message_data.get('caption', '')
                        )

                success_count += 1
                await asyncio.sleep(0.05)  # Telegram limitlaridan qochish

            except Exception as e:
                logger.error(f"Broadcast error for user {user['user_id']}: {e}")

        return success_count

    def run(self):
        """Botni ishga tushirish"""
        # Application yaratish
        self.app = Application.builder().token(self.config.BOT_TOKEN).build()

        # Conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                LANGUAGE_SELECTION: [CallbackQueryHandler(self.language_selection, pattern="^lang_")],
                CHECK_SUBSCRIPTION: [CallbackQueryHandler(self.check_subscription, pattern="^check_subscription$")],
                ENTER_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_code)]
            },
            fallbacks=[CommandHandler("start", self.start)],
            per_user=True
        )

        # Handlerlarni qo'shish
        self.app.add_handler(conv_handler)
        self.app.add_handler(CallbackQueryHandler(self.statistics, pattern="^statistics$"))
        self.app.add_handler(CallbackQueryHandler(self.handlers.back_to_menu, pattern="^back_to_menu$"))
        self.app.add_handler(CallbackQueryHandler(self.handlers.enter_new_code, pattern="^enter_new_code$"))
        self.app.add_handler(CallbackQueryHandler(self.start, pattern="^back_to_start$"))

        # Error handler
        self.app.add_error_handler(self.handlers.error_handler)

        # Botni ishga tushirish
        logger.info("Bot ishga tushdi...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = PromoBot()
    bot.run()