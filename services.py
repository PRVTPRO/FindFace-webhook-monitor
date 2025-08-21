from sqlalchemy.orm import Session
from models import Settings, get_db
from typing import Dict, Any, List
from datetime import datetime

class SettingsService:
    """Сервис для работы с настройками"""
    
    @staticmethod
    def get_settings(db: Session, user_id: str = 'default') -> Dict[str, Any]:
        """Получение настроек пользователя"""
        settings = db.query(Settings).filter(Settings.user_id == user_id).first()
        
        if settings:
            return settings.to_dict()
        else:
            # Возвращаем настройки по умолчанию
            return {
                'timeout': 10,
                'showName': True,
                'showPhoto': True,
                'showCamera': True,
                'showConfidence': True,
                'showTime': True,
                'showHeader': True
            }
    
    @staticmethod
    def save_settings(db: Session, settings_data: Dict[str, Any], user_id: str = 'default') -> bool:
        """Сохранение настроек пользователя"""
        try:
            # Проверяем, существуют ли уже настройки для пользователя
            existing_settings = db.query(Settings).filter(Settings.user_id == user_id).first()
            
            if existing_settings:
                # Обновляем существующие настройки
                existing_settings.timeout = settings_data.get('timeout', 10)
                existing_settings.show_name = settings_data.get('showName', True)
                existing_settings.show_photo = settings_data.get('showPhoto', True)
                existing_settings.show_camera = settings_data.get('showCamera', True)
                existing_settings.show_confidence = settings_data.get('showConfidence', True)
                existing_settings.show_time = settings_data.get('showTime', True)
                existing_settings.show_header = settings_data.get('showHeader', True)
                existing_settings.updated_at = datetime.utcnow()
            else:
                # Создаем новые настройки
                new_settings = Settings.from_dict(settings_data, user_id)
                db.add(new_settings)
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error saving settings: {e}")
            return False
    
    @staticmethod
    def get_all_settings(db: Session) -> List[Dict[str, Any]]:
        """Получение всех настроек (для отладки)"""
        settings = db.query(Settings).order_by(Settings.updated_at.desc()).all()
        
        return [
            {
                'user_id': setting.user_id,
                'timeout': setting.timeout,
                'show_name': setting.show_name,
                'show_photo': setting.show_photo,
                'show_camera': setting.show_camera,
                'show_confidence': setting.show_confidence,
                'show_time': setting.show_time,
                'show_header': setting.show_header,
                'created_at': setting.created_at.isoformat() if setting.created_at else None,
                'updated_at': setting.updated_at.isoformat() if setting.updated_at else None
            }
            for setting in settings
        ]
    
    @staticmethod
    def create_default_settings(db: Session) -> bool:
        """Создание настроек по умолчанию"""
        try:
            # Проверяем, есть ли уже настройки по умолчанию
            default_settings = db.query(Settings).filter(Settings.user_id == 'default').first()
            
            if not default_settings:
                default_data = {
                    'timeout': 10,
                    'showName': True,
                    'showPhoto': True,
                    'showCamera': True,
                    'showConfidence': True,
                    'showTime': True,
                    'showHeader': True
                }
                
                new_settings = Settings.from_dict(default_data, 'default')
                db.add(new_settings)
                db.commit()
                print("✅ Настройки по умолчанию созданы")
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error creating default settings: {e}")
            return False
