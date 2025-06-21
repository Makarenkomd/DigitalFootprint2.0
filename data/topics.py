import sqlalchemy
from flask_login import UserMixin


from .db_session import SqlAlchemyBase


class Topic(SqlAlchemyBase, UserMixin):
    __tablename__ = "topics"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
