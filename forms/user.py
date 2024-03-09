from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField, DateField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    # email = EmailField('Почта', validators=[DataRequired()])
    date_of_birth = DateField('Дата рождения', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    # about = TextAreaField("Немного о себе")
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    # email = EmailField('Почта', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    # password = PasswordField('Пароль', validators=[DataRequired()])
    date_of_birth = DateField('Дата рождения', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
