from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, DateField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    date_of_birth = DateField('Дата рождения', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    date_of_birth = DateField('Дата рождения', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
