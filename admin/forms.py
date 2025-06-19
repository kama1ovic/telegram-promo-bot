"""
Flask admin panel uchun formlar
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    """Login formasi"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Parol', validators=[DataRequired()])
    remember = BooleanField('Meni eslab qol')
    submit = SubmitField('Kirish')

class CodeForm(FlaskForm):
    """Kod qo'shish formasi"""
    codes = TextAreaField('Kodlar (har bir qatorda bitta)',
                         validators=[DataRequired()],
                         render_kw={'rows': 10, 'placeholder': '9a8JP1cn9\nAB123456\n...'})
    is_winning = BooleanField('Yutuqli kodlar')
    submit = SubmitField('Qo\'shish')

class BroadcastForm(FlaskForm):
    """Xabar yuborish formasi"""
    message = TextAreaField('Xabar matni',
                           validators=[DataRequired()],
                           render_kw={'rows': 5})
    file = FileField('Fayl (ixtiyoriy)',
                     validators=[FileAllowed(['jpg', 'png', 'gif', 'pdf', 'doc', 'docx', 'zip'])])
    submit = SubmitField('Yuborish')