from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Boolean,
    Table,
    select,
    JSON, 
    TIMESTAMP
)
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import BYTEA, JSONB
from datetime import datetime

from uuid import uuid4
from sqlalchemy.orm import relationship, Mapped, mapped_column

db = SQLAlchemy()

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
        db.session.commit()
        # try:
        #     db.session.commit()
        # except Exception as e:
        #     print("Ошибка при коммите сессии: ", e)


class Generator(db.Model):
    __tablename__ = 'Generator'
    generator_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid4()),
        primary_key=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey('User.user_id'),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    original_dataset: Mapped[bytes] = mapped_column(BYTEA)
    original_metadata: Mapped[dict] = mapped_column(JSONB)
    parameters: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP')
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP'),
        onupdate=text('CURRENT_TIMESTAMP')
    )
    user = relationship('User', backref='generators')

    def __init__(self, user_id, name, original_dataset, original_metadata, parameters):
        self.user_id = user_id
        self.name = name
        self.original_dataset = original_dataset
        self.original_metadata = original_metadata
        self.parameters = parameters

    @staticmethod
    def add_generator(user_id, name, original_dataset, original_metadata, parameters):
        new_generator = Generator(
            user_id=user_id,
            name=name,
            original_dataset=original_dataset,
            original_metadata=original_metadata,
            parameters=parameters
        )
        db.session.add(new_generator)
        try:
            db.session.commit()
        except Exception as e:
            print("Ошибка при коммите сессии: ", e)

    # created_at: Mapped[datetime] = mapped_column(default=db.func.current_timestamp())
    # updated_at: Mapped[datetime] = mapped_column(default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
