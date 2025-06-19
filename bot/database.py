"""
Database operatsiyalari
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional
import threading

class Database:
    def __init__(self, db_path: str = "promo_bot.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._create_tables()

    def _get_connection(self):
        """Database connection olish"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """Jadvallarni yaratish"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Foydalanuvchilar jadvali
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    phone_number TEXT,
                    language TEXT DEFAULT 'uz',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Kodlar jadvali
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    is_winning BOOLEAN DEFAULT 0,
                    is_used BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Kod ishlatilishi jadvali
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS code_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    code_id INTEGER NOT NULL,
                    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (code_id) REFERENCES codes(id)
                )
            """)

            # Admin jadvali
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()

    def add_user(self, user_id: int, username: str = None,
                 first_name: str = None, last_name: str = None) -> bool:
        """Yangi foydalanuvchi qo'shish"""
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT OR IGNORE INTO users 
                    (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                """, (user_id, username, first_name, last_name))

                # Agar foydalanuvchi mavjud bo'lsa, ma'lumotlarni yangilash
                if cursor.rowcount == 0:
                    cursor.execute("""
                        UPDATE users 
                        SET username = ?, first_name = ?, last_name = ?, 
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    """, (username, first_name, last_name, user_id))

                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Add user error: {e}")
                return False

    def update_user_language(self, user_id: int, language: str) -> bool:
        """Foydalanuvchi tilini yangilash"""
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE users 
                    SET language = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (language, user_id))

                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Update language error: {e}")
                return False

    def add_code(self, code: str, is_winning: bool = False) -> bool:
        """Yangi kod qo'shish"""
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO codes (code, is_winning)
                    VALUES (?, ?)
                """, (code, is_winning))

                conn.commit()
                conn.close()
                return True
            except sqlite3.IntegrityError:
                # Kod allaqachon mavjud
                return False
            except Exception as e:
                print(f"Add code error: {e}")
                return False

    def check_and_use_code(self, user_id: int, code: str) -> Dict:
        """Kodni tekshirish va ishlatish"""
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                # Kodni topish
                cursor.execute("""
                    SELECT id, is_winning, is_used 
                    FROM codes 
                    WHERE code = ?
                """, (code,))

                code_data = cursor.fetchone()

                if not code_data:
                    conn.close()
                    return {'status': 'invalid', 'is_winning': False}

                code_id = code_data['id']
                is_winning = code_data['is_winning']
                is_used = code_data['is_used']

                # Agar kod allaqachon ishlatilgan bo'lsa
                if is_used:
                    conn.close()
                    return {'status': 'already_used', 'is_winning': False}

                # Kodni ishlatilgan deb belgilash
                cursor.execute("""
                    UPDATE codes 
                    SET is_used = 1 
                    WHERE id = ?
                """, (code_id,))

                # Foydalanish tarixiga qo'shish
                cursor.execute("""
                    INSERT INTO code_usage (user_id, code_id)
                    VALUES (?, ?)
                """, (user_id, code_id))

                conn.commit()
                conn.close()

                return {
                    'status': 'success',
                    'is_winning': bool(is_winning)
                }

            except Exception as e:
                print(f"Check code error: {e}")
                return {'status': 'error', 'is_winning': False}

    def get_user_statistics(self, user_id: int) -> Dict:
        """Foydalanuvchi statistikasini olish"""
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                # Umumiy kodlar soni
                cursor.execute("""
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN c.is_winning = 1 THEN 1 ELSE 0 END) as winning,
                           SUM(CASE WHEN c.is_winning = 0 THEN 1 ELSE 0 END) as losing,
                           MIN(cu.used_at) as first_code,
                           MAX(cu.used_at) as last_code
                    FROM code_usage cu
                    JOIN codes c ON cu.code_id = c.id
                    WHERE cu.user_id = ?
                """, (user_id,))

                stats = cursor.fetchone()
                conn.close()

                return {
                    'total_codes': stats['total'] or 0,
                    'winning_codes': stats['winning'] or 0,
                    'losing_codes': stats['losing'] or 0,
                    'first_code_date': stats['first_code'],
                    'last_code_date': stats['last_code']
                }

            except Exception as e:
                print(f"Get statistics error: {e}")
                return {
                    'total_codes': 0,
                    'winning_codes': 0,
                    'losing_codes': 0,
                    'first_code_date': None,
                    'last_code_date': None
                }

    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Foydalanuvchi ma'lumotlarini olish"""
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT * FROM users WHERE user_id = ?
                """, (user_id,))

                user = cursor.fetchone()
                conn.close()

                if user:
                    return dict(user)
                return None

            except Exception as e:
                print(f"Get user info error: {e}")
                return None

    def get_all_users(self) -> List[Dict]:
        """Barcha foydalanuvchilarni olish"""
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM users")

                users = [dict(row) for row in cursor.fetchall()]
                conn.close()

                return users

            except Exception as e:
                print(f"Get all users error: {e}")
                return []

    def get_all_codes(self, filter_type: str = None) -> List[Dict]:
        """Barcha kodlarni olish"""
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                query = "SELECT * FROM codes"
                params = []

                if filter_type == 'winning':
                    query += " WHERE is_winning = 1"
                elif filter_type == 'used':
                    query += " WHERE is_used = 1"

                query += " ORDER BY created_at DESC"

                cursor.execute(query, params)

                codes = [dict(row) for row in cursor.fetchall()]
                conn.close()

                return codes

            except Exception as e:
                print(f"Get all codes error: {e}")
                return []

    def get_code_usage_stats(self) -> List[Dict]:
        """Kod ishlatilishi statistikasi"""
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT 
                        u.user_id,
                        u.username,
                        u.first_name,
                        u.last_name,
                        u.phone_number,
                        COUNT(cu.id) as code_count,
                        SUM(CASE WHEN c.is_winning = 1 THEN 1 ELSE 0 END) as winning_count,
                        MAX(cu.used_at) as last_used
                    FROM users u
                    LEFT JOIN code_usage cu ON u.user_id = cu.user_id
                    LEFT JOIN codes c ON cu.code_id = c.id
                    GROUP BY u.user_id
                    ORDER BY code_count DESC
                """)

                stats = [dict(row) for row in cursor.fetchall()]
                conn.close()

                return stats

            except Exception as e:
                print(f"Get code usage stats error: {e}")
                return []

    def add_admin(self, username: str, password_hash: str) -> bool:
        """Admin qo'shish"""
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO admins (username, password_hash)
                    VALUES (?, ?)
                """, (username, password_hash))

                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Add admin error: {e}")
                return False

    def get_admin(self, username: str) -> Optional[Dict]:
        """Admin ma'lumotlarini olish"""
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT * FROM admins WHERE username = ?
                """, (username,))

                admin = cursor.fetchone()
                conn.close()

                if admin:
                    return dict(admin)
                return None

            except Exception as e:
                print(f"Get admin error: {e}")
                return None