from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class GroupForm(FlaskForm):
    name = StringField(
        "Название группы",
        validators=[
            DataRequired(),
            Length(
                4,
                64,
            ),
        ],
    )

    submit = SubmitField("Подтвердить")
