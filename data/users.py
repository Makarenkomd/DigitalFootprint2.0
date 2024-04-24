import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    group = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='default')
    date_of_birth = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    user_level = sqlalchemy.Column(sqlalchemy.String, default='student')

    avatar = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='icon.jpg')
