from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class AddQuestionForm(FlaskForm):
    text = StringField(
        "Название группы",
        validators=[
            DataRequired(),
            Length(
                5,
                64,
            ),
        ],
    )

    submit = SubmitField("Подтвердить")
