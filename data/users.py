import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Group(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "groups"

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False,
    )


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "users"

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=True,
    )

    group_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey(
            "groups.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    date_of_birth = sqlalchemy.Column(
        sqlalchemy.Date,
        nullable=False,
    )
    user_level = sqlalchemy.Column(
        sqlalchemy.String,
        default="student",
    )