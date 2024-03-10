import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class BlitzTest(SqlAlchemyBase, UserMixin):
    __tablename__ = 'blitz_tests'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    question_1 = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('questions.id'))
    question_2 = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('questions.id'))
    question_3 = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('questions.id'))
    question_4 = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('questions.id'))
    question_5 = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('questions.id'))

    answer_1 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    answer_2 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    answer_3 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    answer_4 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    answer_5 = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    comment_1 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    comment_2 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    comment_3 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    comment_4 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    comment_5 = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    student = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
