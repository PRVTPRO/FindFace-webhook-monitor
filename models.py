from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Создаем базовый класс для моделей
Base = declarative_base()

class Settings(Base):
    """Модель настроек пользователя"""
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), unique=True, nullable=False, default='default')
    timeout = Column(Integer, nullable=False, default=10)
    show_name = Column(Boolean, nullable=False, default=True)
    show_photo = Column(Boolean, nullable=False, default=True)
    show_camera = Column(Boolean, nullable=False, default=True)
    show_confidence = Column(Boolean, nullable=False, default=True)
    show_time = Column(Boolean, nullable=False, default=True)
    show_header = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Преобразование модели в словарь"""
        return {
            'timeout': self.timeout,
            'showName': self.show_name,
            'showPhoto': self.show_photo,
            'showCamera': self.show_camera,
            'showConfidence': self.show_confidence,
            'showTime': self.show_time,
            'showHeader': self.show_header
        }
    
    @classmethod
    def from_dict(cls, data, user_id='default'):
        """Создание модели из словаря"""
        return cls(
            user_id=user_id,
            timeout=data.get('timeout', 10),
            show_name=data.get('showName', True),
            show_photo=data.get('showPhoto', True),
            show_camera=data.get('showCamera', True),
            show_confidence=data.get('showConfidence', True),
            show_time=data.get('showTime', True),
            show_header=data.get('showHeader', True)
        )

# Создаем движок базы данных
DATABASE_URL = "sqlite:///./settings.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем таблицы
Base.metadata.create_all(bind=engine)

def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
