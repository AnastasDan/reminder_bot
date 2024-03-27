import os

from dotenv import load_dotenv
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_PORT = os.getenv("DB_PORT")
DB_HOST = os.getenv("DB_HOST")

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)
Base = declarative_base()


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    welcomed = Column(Boolean, default=False)

    reminders = relationship("Reminder", back_populates="user")


class Reminder(Base):
    """Модель напоминания."""

    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, index=True)
    time = Column(DateTime, index=True)
    message = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="reminders")


async def init_db():
    """Инициализация базы данных."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
