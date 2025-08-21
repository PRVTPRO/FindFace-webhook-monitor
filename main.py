from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from datetime import datetime, timedelta
import asyncio
from typing import List, Dict, Any
import uuid
import threading
import time
from sqlalchemy.orm import Session
from models import get_db
from services import SettingsService
from contextlib import asynccontextmanager

# Lifespan контекст для инициализации
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Инициализация приложения...")    
    
    
    # Создаем настройки по умолчанию при первом запуске
    db = next(get_db())
    try:
        SettingsService.create_default_settings(db)
        print("✅ Настройки по умолчанию созданы")
        print("🚀 Запуск Notification Mark...")
        print("📱 Приложение будет доступно по адресу: http://localhost:8000")
        print("🔗 API документация: http://localhost:8000/docs")
        print("📡 Webhook endpoint: http://localhost:8000/ntf")
        print()
        print("Для остановки нажмите Ctrl+C")
        print("-" * 50)
    except Exception as e:
        print(f"❌ Ошибка создания настроек: {e}")
    finally:
        db.close()
    
    yield
    
    # Shutdown
    print("🛑 Завершение работы приложения...")

app = FastAPI(title="Notification Mark", lifespan=lifespan)

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")

# Хранилище уведомлений в памяти (в продакшене лучше использовать Redis или БД)
notifications: List[Dict[str, Any]] = []

def cleanup_expired_notifications():
    """Фоновая задача для очистки устаревших уведомлений"""
    while True:
        current_time = datetime.now()
        # Удаляем уведомления старше 10 секунд (или настраиваемого времени)
        global notifications
        notifications = [
            n for n in notifications 
            if current_time - datetime.fromisoformat(n['timestamp']) < timedelta(seconds=10)
        ]
        time.sleep(1)  # Проверяем каждую секунду

# Запускаем фоновую задачу очистки
cleanup_thread = threading.Thread(target=cleanup_expired_notifications, daemon=True)
cleanup_thread.start()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница с уведомлениями"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    """Страница настроек"""
    return templates.TemplateResponse("settings.html", {"request": request})

@app.post("/ntf")
async def webhook_handler(request: Request):
    """Обработчик вебхука"""
    try:
        data = await request.json()
        
        # Отладочная информация
        print("Received webhook data:", data)
        
        # Обрабатываем данные вебхука
        if isinstance(data, list):
            for item in data:
                if item.get('matched_card') and item['matched_card'].get('name'):
                    # Отладочная информация для thumbnail
                    thumbnail = item.get('thumbnail', '')
                    print(f"Processing notification for {item['matched_card']['name']}")
                    print(f"Thumbnail URL: {thumbnail}")
                    print(f"Thumbnail type: {type(thumbnail)}")
                    print(f"Thumbnail length: {len(thumbnail) if thumbnail else 0}")
                    
                    notification = {
                        'id': str(uuid.uuid4()),
                        'name': item['matched_card']['name'],
                        'timestamp': datetime.now().isoformat(),
                        'confidence': item.get('confidence', 0),
                        'camera_name': item.get('camera', {}).get('name', 'Неизвестная камера'),
                        'created_date': item.get('created_date', ''),
                        'thumbnail': thumbnail,
                        'fullframe': item.get('fullframe', '')
                    }
                    
                    print(f"Created notification: {notification}")
                    notifications.append(notification)
                    
                    # Ограничиваем количество уведомлений в памяти
                    if len(notifications) > 100:
                        notifications.pop(0)
        
        return {"status": "success", "message": "Notification received"}
    
    except Exception as e:
        print(f"Error in webhook handler: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/notifications")
async def get_notifications():
    """API для получения уведомлений"""
    return {"notifications": notifications}

@app.get("/api/settings")
async def get_settings(db: Session = Depends(get_db)):
    """API для получения настроек из базы данных"""
    return SettingsService.get_settings(db)

@app.post("/api/settings")
async def save_settings(request: Request, db: Session = Depends(get_db)):
    """API для сохранения настроек в базу данных"""
    try:
        data = await request.json()
        success = SettingsService.save_settings(db, data)
        
        if success:
            return {"status": "success", "message": "Settings saved"}
        else:
            return {"status": "error", "message": "Failed to save settings"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/settings/debug")
async def get_debug_settings(db: Session = Depends(get_db)):
    """API для получения всех настроек (отладка)"""
    return {"settings": SettingsService.get_all_settings(db)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
