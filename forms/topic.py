from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddTopicForm(FlaskForm):
    name = StringField('Название темы', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
