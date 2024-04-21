from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Boolean,
    Table,
    select,
    JSON
)
from uuid import uuid4
from sqlalchemy.orm import relationship, Mapped, mapped_column

db = SQLAlchemy()

class Base(db.Model):
    __abstract__ = True
    # created_at: Mapped[datetime] = mapped_column(default=db.func.current_timestamp())
    # updated_at: Mapped[datetime] = mapped_column(default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


class User(db.Model):
    __tablename__ = 'User'
    user_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid4()),
        primary_key=True,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    yandex_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    def __init__(self, first_name, last_name, yandex_id):
        self.first_name = first_name
        self.last_name = last_name
        self.yandex_id = yandex_id


    @staticmethod
    def add_user(first_name, last_name, yandex_id):
        new_user = User(first_name=first_name, last_name=last_name, yandex_id=yandex_id)
        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as e:
            print("Ошибка при коммите сессии: ", e)