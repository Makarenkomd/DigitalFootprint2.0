from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    date_of_birth = DateField(
        "Дата рождения",
        validators=[
            DataRequired(),
        ],
    )
    name = StringField(
        "Имя пользователя",
        validators=[
            DataRequired(),
        ],
    )
    group = SelectField(
        "Группа",
        coerce=int,
        validators=[
            DataRequired(),
        ],
    )
    submit = SubmitField(
        "Зарегистрироваться",
    )


class LoginForm(FlaskForm):
    name = StringField(
        "Имя пользователя",
        validators=[
            DataRequired(),
        ],
    )
    date_of_birth = DateField(
        "Дата рождения",
        validators=[
            DataRequired(),
        ],
    )
    remember_me = BooleanField(
        "Запомнить меня",
    )
    submit = SubmitField(
        "Войти",
    )


class ProfileForm(FlaskForm):
    name = StringField(
        "Имя пользователя",
        validators=[
            DataRequired(),
        ],
    )
    date_of_birth = DateField(
        "Дата рождения",
        validators=[
            DataRequired(),
        ],
    )
    group = SelectField(
        "Группа",
        coerce=int,
        validators=[
            DataRequired(),
        ],
    )
    submit = SubmitField(
        "Сохранить",
    )
