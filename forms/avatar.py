from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import SubmitField


class AvatarForm(FlaskForm):
    avatar = FileField(
        "Загрузить аватар",
        validators=[
            FileAllowed(
                [
                    "jpg",
                    "png",
                ],
                "Только изображения",
            ),
        ],
    )
    submit = SubmitField("Отправить")
