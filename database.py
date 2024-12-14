# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL подключения к PostgreSQL


DATABASE_URL = "postgresql://postgres:pass123@localhost/postgres"

# Создаем движок и сессию для работы с базой данных
engine = create_engine(DATABASE_URL, echo=True)

# Создаем сессионный объект
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для моделей
Base = declarative_base()

# Функция для инициализации базы данных
def init_db():
    # Создание таблиц, если они не существуют
    Base.metadata.create_all(bind=engine)