# Telegram Promo Bot va Admin Panel

Bu loyiha Telegram bot va Flask admin paneldan iborat bo'lib, promokodlarni boshqarish uchun mo'ljallangan.

## 📋 Xususiyatlar

### Telegram Bot
- 🌐 O'zbek va Rus tillarini qo'llab-quvvatlash
- 📢 Telegram kanaliga majburiy obuna
- 🎫 8 xonali promokodlarni tekshirish
- 📊 Foydalanuvchi statistikasi
- 🎉 Yutuqli kodlar uchun admin bildirishnomasi

### Admin Panel
- 🔐 Xavfsiz login tizimi
- 📝 Kodlarni boshqarish (qo'shish, ko'rish, filtrlash)
- 👥 Foydalanuvchilar statistikasi
- 📨 Ommaviy xabar yuborish
- 📊 CSV eksport funksiyasi

## 🚀 O'rnatish (Local)

### 1. Talablar
- Python 3.12.7 yoki yangi versiya
- pip (Python package manager)
- SQLite3 (default) yoki PostgreSQL
- Ubuntu OS (tavsiya etiladi)

### 2. Loyihani klonlash

```bash
# Loyiha papkasini yaratish
mkdir telegram-promo-bot
cd telegram-promo-bot

# Barcha fayllarni ko'chiring yoki yarating
```

### 3. Virtual muhit yaratish

```bash
# Virtual muhit yaratish
python3 -m venv venv

# Virtual muhitni faollashtirish
source venv/bin/activate  # Ubuntu/Linux uchun
```

### 4. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 5. Telegram Bot yaratish

1. Telegram'da [@BotFather](https://t.me/botfather) ga o'ting
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting (masalan: "Promo Kod Bot")
4. Bot username kiriting (masalan: @promo_kod_bot)
5. Bot tokenini oling va saqlang

### 6. Telegram kanal yaratish

1. Telegram'da yangi kanal yarating
2. Kanalga nom bering va username belgilang (masalan: @sizning_kanalingiz)
3. Kanal ID sini olish:
   - Kanalga biror xabar yuboring
   - [@userinfobot](https://t.me/userinfobot) ga kanaldan xabar forward qiling
   - Kanal ID sini oling (-1001234567890 ko'rinishida)

### 7. .env faylini sozlash

`.env` faylini yarating va quyidagi ma'lumotlarni kiriting:

```env
# Telegram Bot
BOT_TOKEN=sizning_bot_tokeningiz
CHANNEL_ID=@sizning_kanalingiz
CHANNEL_CHAT_ID=-1001234567890
ADMIN_TELEGRAM_ID=sizning_telegram_id

# Database
DATABASE_URL=sqlite:///promo_bot.db

# Flask
SECRET_KEY=juda-maxfiy-kalit-yarating
FLASK_ENV=development

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=kuchli_parol_kiriting
```

**Telegram ID ni olish:**
- [@userinfobot](https://t.me/userinfobot) ga `/start` yuboring
- Sizning ID ko'rsatiladi

**SECRET_KEY yaratish:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 8. Loyihani ishga tushirish

**Telegram botni ishga tushirish:**
```bash
python3 run_bot.py
```

**Admin panelni ishga tushirish (yangi terminal):**
```bash
python3 run_admin.py
```

Admin panel: http://localhost:5000

## 📦 Deploy qilish (Production)

### VPS Server talablari
- Ubuntu 20.04 LTS yoki yangi
- Minimum 1GB RAM
- 10GB disk
- Python 3.12.7+

### 1. Serverga ulanish

```bash
ssh root@server_ip_manzil
```

### 2. Tizimni yangilash

```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Kerakli dasturlarni o'rnatish

```bash
# Python va kerakli paketlar
sudo apt install python3.12 python3.12-venv python3.12-dev python3-pip -y

# PostgreSQL (agar kerak bo'lsa)
sudo apt install postgresql postgresql-contrib -y

# Nginx
sudo apt install nginx -y

# Supervisor (jarayonlarni boshqarish)
sudo apt install supervisor -y
```

### 4. PostgreSQL sozlash (ixtiyoriy)

```bash
# PostgreSQL ga kirish
sudo -u postgres psql

# Database yaratish
CREATE DATABASE promo_bot_db;
CREATE USER promo_bot_user WITH PASSWORD 'kuchli_parol';
GRANT ALL PRIVILEGES ON DATABASE promo_bot_db TO promo_bot_user;
\q
```

### 5. Loyihani serverga ko'chirish

```bash
# Loyiha papkasini yaratish
sudo mkdir -p /var/www/promo-bot
sudo chown $USER:$USER /var/www/promo-bot

# Fayllarni ko'chirish (local kompyuterdan)
scp -r * root@server_ip:/var/www/promo-bot/
```

### 6. Virtual muhit yaratish (serverda)

```bash
cd /var/www/promo-bot
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 7. .env faylini sozlash (serverda)

```bash
nano .env
```

Production uchun .env:
```env
# Telegram Bot
BOT_TOKEN=sizning_bot_tokeningiz
CHANNEL_ID=@sizning_kanalingiz
CHANNEL_CHAT_ID=-1001234567890
ADMIN_TELEGRAM_ID=sizning_telegram_id

# Database (PostgreSQL)
DATABASE_URL=postgresql://promo_bot_user:kuchli_parol@localhost/promo_bot_db

# Flask
SECRET_KEY=yangi-maxfiy-kalit-yarating
FLASK_ENV=production

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=juda_kuchli_parol
```

### 8. Supervisor sozlash

Bot uchun supervisor config:
```bash
sudo nano /etc/supervisor/conf.d/promo_bot.conf
```

```ini
[program:promo_bot]
command=/var/www/promo-bot/venv/bin/python /var/www/promo-bot/run_bot.py
directory=/var/www/promo-bot
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/promo_bot.log
environment=PATH="/var/www/promo-bot/venv/bin"
```

Admin panel uchun:
```bash
sudo nano /etc/supervisor/conf.d/promo_admin.conf
```

```ini
[program:promo_admin]
command=/var/www/promo-bot/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 admin.app:app
directory=/var/www/promo-bot
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/promo_admin.log
environment=PATH="/var/www/promo-bot/venv/bin"
```

### 9. Nginx sozlash

```bash
sudo nano /etc/nginx/sites-available/promo-bot
```

```nginx
server {
    listen 80;
    server_name sizning-domain.uz;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/promo-bot/static;
    }
}
```

```bash
# Nginx configni faollashtirish
sudo ln -s /etc/nginx/sites-available/promo-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 10. Xizmatlarni ishga tushirish

```bash
# Supervisor yangilash va ishga tushirish
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start promo_bot
sudo supervisorctl start promo_admin

# Status tekshirish
sudo supervisorctl status
```

### 11. SSL sertifikat (Let's Encrypt)

```bash
# Certbot o'rnatish
sudo apt install certbot python3-certbot-nginx -y

# SSL sertifikat olish
sudo certbot --nginx -d sizning-domain.uz
```

## 🔧 Foydalanish

### Bot bilan ishlash
1. Telegram'da botingizni toping
2. `/start` buyrug'ini yuboring
3. Tilni tanlang
4. Kanalga obuna bo'ling
5. 8 xonali kodni kiriting

### Admin panel
1. https://sizning-domain.uz ga kiring
2. Username va parol kiriting
3. Kodlarni qo'shing (har bir qatorda bitta)
4. Foydalanuvchilar statistikasini ko'ring
5. Kerak bo'lsa xabar yuboring

## 🛠️ Muammolarni hal qilish

### Bot ishlamayapti
```bash
# Log fayllarni tekshirish
sudo tail -f /var/log/promo_bot.log

# Botni qayta ishga tushirish
sudo supervisorctl restart promo_bot
```

### Admin panel ochilmayapti
```bash
# Nginx loglarini tekshirish
sudo tail -f /var/log/nginx/error.log

# Admin panel qayta ishga tushirish
sudo supervisorctl restart promo_admin
```

### Database xatolari
```bash
# SQLite faylini tekshirish
ls -la promo_bot.db

# PostgreSQL holatini tekshirish
sudo systemctl status postgresql
```

## 📊 Monitoring

### Jarayonlar holatini ko'rish
```bash
sudo supervisorctl status
```

### Server resurslarini ko'rish
```bash
htop  # yoki top
```

### Disk joyini tekshirish
```bash
df -h
```

## 🔐 Xavfsizlik

1. **Parollar**: Kuchli parollar ishlating
2. **Firewall**: Faqat kerakli portlarni oching
3. **Updates**: Tizimni muntazam yangilab turing
4. **Backup**: Database ni muntazam backup qiling

### Firewall sozlash
```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

## 📝 Kod misollari

### Yangi kod qo'shish (Python)
```python
from bot.database import Database

db = Database()
db.add_code("12345678", is_winning=True)
```

### Foydalanuvchilar ro'yxati olish
```python
users = db.get_all_users()
for user in users:
    print(f"{user['first_name']} - {user['username']}")
```

## 🤝 Yordam

Agar muammo bo'lsa:
1. Loglarni tekshiring
2. .env faylini to'g'ri sozlanganini tekshiring
3. Python versiyasini tekshiring: `python3 --version`
4. Barcha kutubxonalar o'rnatilganini tekshiring

Muvaffaqiyat! 🎉