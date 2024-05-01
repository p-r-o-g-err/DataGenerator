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
    table_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dataset_location: Mapped[str] = mapped_column(String(1000))
    dataset_metadata = Column(JSONB)
    model_config = Column(JSONB)
    model_location: Mapped[str] = mapped_column(String(1000))
    model_training_status = Column(JSONB)
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

    def __init__(self, user_id, name, table_name, dataset_location, dataset_metadata, model_config):
        self.user_id = user_id
        self.name = name
        self.table_name = table_name
        self.dataset_location = dataset_location
        self.dataset_metadata = dataset_metadata
        self.model_config = model_config
        self.model_location = None
        self.model_training_status = {}
        

    @staticmethod
    def add_generator(user_id, name, table_name, dataset_location = None, dataset_metadata = {}, model_config = {}):
        new_generator = Generator(
            user_id=user_id,
            name=name,
            table_name=table_name,
            dataset_location=dataset_location,
            dataset_metadata=dataset_metadata,
            model_config=model_config
        )
        db.session.add(new_generator)
        try:
            db.session.commit()
            return new_generator
        except Exception as e:
            print("Ошибка при коммите сессии: ", e)
            print("Подробности об ошибке: ", e.__traceback__)

    # created_at: Mapped[datetime] = mapped_column(default=db.func.current_timestamp())
    # updated_at: Mapped[datetime] = mapped_column(default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
