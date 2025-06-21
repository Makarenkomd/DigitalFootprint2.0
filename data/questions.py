import sqlalchemy
from flask_login import UserMixin


from .db_session import SqlAlchemyBase


class Question(SqlAlchemyBase, UserMixin):
    __tablename__ = "questions"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    topic_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("topics.id"), nullable=True)
