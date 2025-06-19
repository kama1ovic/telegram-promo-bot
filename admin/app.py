"""
Flask Admin Panel
"""

from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import sys
import io

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.database import Database
from bot.config import Config
from admin.models import User
from admin.forms import LoginForm, CodeForm, BroadcastForm
import asyncio
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Database
db = Database()

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Iltimos, avval tizimga kiring.'

# Bot instance (for broadcasting)
bot_instance = None


def set_bot_instance(bot):
    global bot_instance
    bot_instance = bot


@login_manager.user_loader
def load_user(user_id):
    admin = db.get_admin(user_id)
    if admin:
        return User(admin['username'])
    return None


# Admin yaratish (agar mavjud bo'lmasa)
def create_default_admin():
    admin = db.get_admin(Config.ADMIN_USERNAME)
    if not admin:
        password_hash = generate_password_hash(Config.ADMIN_PASSWORD)
        db.add_admin(Config.ADMIN_USERNAME, password_hash)
        print(f"Default admin created: {Config.ADMIN_USERNAME}")


@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        admin = db.get_admin(form.username.data)
        if admin and check_password_hash(admin['password_hash'], form.password.data):
            user = User(admin['username'])
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Noto\'g\'ri username yoki parol!', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Statistika ma'lumotlari
    stats = {
        'total_users': len(db.get_all_users()),
        'total_codes': len(db.get_all_codes()),
        'used_codes': len(db.get_all_codes('used')),
        'winning_codes': len(db.get_all_codes('winning')),
    }

    # Oxirgi 7 kunlik statistika
    users = db.get_all_users()
    recent_users = 0
    week_ago = datetime.now() - timedelta(days=7)

    for user in users:
        if user.get('created_at'):
            user_date = datetime.strptime(user['created_at'], '%Y-%m-%d %H:%M:%S')
            if user_date > week_ago:
                recent_users += 1

    stats['recent_users'] = recent_users

    return render_template('dashboard.html', stats=stats)


@app.route('/codes', methods=['GET', 'POST'])
@login_required
def codes():
    form = CodeForm()

    if form.validate_on_submit():
        codes_text = form.codes.data.strip()
        is_winning = form.is_winning.data

        # Kodlarni qatorlarga bo'lish
        codes_list = [code.strip() for code in codes_text.split('\n') if code.strip()]

        success_count = 0
        for code in codes_list:
            if len(code) == 8:  # 8 xonali kod
                if db.add_code(code, is_winning):
                    success_count += 1

        flash(f'{success_count} ta kod muvaffaqiyatli qo\'shildi!', 'success')
        return redirect(url_for('codes'))

    # Kodlar ro'yxati
    filter_type = request.args.get('filter')
    all_codes = db.get_all_codes(filter_type)

    return render_template('codes.html', form=form, codes=all_codes, filter_type=filter_type)


@app.route('/users')
@login_required
def users():
    # Foydalanuvchilar statistikasi
    users_stats = db.get_code_usage_stats()

    # Filtr
    date_filter = request.args.get('date')
    if date_filter:
        # Sana bo'yicha filtrlash logikasi
        pass

    return render_template('users.html', users=users_stats)


@app.route('/broadcast', methods=['GET', 'POST'])
@login_required
def broadcast():
    form = BroadcastForm()

    if form.validate_on_submit():
        message_data = {
            'text': form.message.data
        }

        # Fayl yuklash
        if form.file.data:
            file = form.file.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            message_data['file_path'] = file_path
            message_data['caption'] = form.message.data

        # Xabar yuborish (background task)
        def send_broadcast():
            if bot_instance:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(bot_instance.broadcast_message(message_data))
                flash(f'{result} ta foydalanuvchiga xabar yuborildi!', 'success')
            else:
                flash('Bot ulanmagan!', 'danger')

        thread = threading.Thread(target=send_broadcast)
        thread.start()

        flash('Xabar yuborish boshlandi!', 'info')
        return redirect(url_for('broadcast'))

    return render_template('broadcast.html', form=form)


@app.route('/export/codes')
@login_required
def export_codes():
    """Kodlarni CSV formatda eksport qilish"""
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow(['Kod', 'Yutuqli', 'Ishlatilgan', 'Yaratilgan vaqt'])

    # Data
    codes = db.get_all_codes()
    for code in codes:
        writer.writerow([
            code['code'],
            'Ha' if code['is_winning'] else 'Yo\'q',
            'Ha' if code['is_used'] else 'Yo\'q',
            code['created_at']
        ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'codes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )


@app.route('/export/users')
@login_required
def export_users():
    """Foydalanuvchilarni CSV formatda eksport qilish"""
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow(
        ['User ID', 'Username', 'Ism', 'Familiya', 'Telefon', 'Kodlar soni', 'Yutuqli kodlar', 'Oxirgi faollik'])

    # Data
    users = db.get_code_usage_stats()
    for user in users:
        writer.writerow([
            user['user_id'],
            f"@{user['username']}" if user['username'] else '',
            user['first_name'] or '',
            user['last_name'] or '',
            user['phone_number'] or '',
            user['code_count'],
            user['winning_count'],
            user['last_used'] or ''
        ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.before_request
def before_request():
    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response


if __name__ == '__main__':
    Config.init_app()
    create_default_admin()
    app.run(debug=True, port=5000)