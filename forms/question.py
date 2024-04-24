from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddQuestionForm(FlaskForm):
    text = StringField('Текст вопроса', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
