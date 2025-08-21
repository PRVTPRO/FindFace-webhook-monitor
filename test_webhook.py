import requests
import json
import time

def test_webhook():
    """Тестовый скрипт для проверки работы вебхука"""
    
    webhook_url = "http://localhost:8000/ntf"
    
    # Тестовые данные
    test_data = [
        {
            "matched_card": {"name": "Simple 3"},
            "confidence": 0.92,
            "camera": {"name": "Test 3"},
            "created_date": "2025-08-21T08:16:23+00:00",
            "thumbnail": "https://via.placeholder.com/150x150/EF4444/FFFFFF?text=Face"
        },
        {
            "matched_card": {"name": "Simple 2"},
            "confidence": 0.87,
            "camera": {"name": "Test 2"},
            "created_date": "2025-08-21T08:17:45+00:00",
            "thumbnail": "https://via.placeholder.com/150x150/EF4444/FFFFFF?text=Face",
            "fullframe": "https://via.placeholder.com/400x300/DC2626/FFFFFF?text=Event+Photo"
        },
        {
            "matched_card": {"name": "Myyy"},
            "confidence": 0.95,
            "camera": {"name": "Test"},
            "created_date": "2025-08-21T08:18:12+00:00",
            "thumbnail": "https://via.placeholder.com/150x150/8B5CF6/FFFFFF?text=Face",
            "fullframe": "https://via.placeholder.com/400x300/7C3AED/FFFFFF?text=Event+Photo"
        }
    ]
    
    print("🚀 Тестирование вебхука...")
    print(f"URL: {webhook_url}")
    print(f"Количество тестовых уведомлений: {len(test_data)}")
    
    try:
        # Отправляем данные
        response = requests.post(
            webhook_url, 
            json=test_data, 
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Данные успешно отправлены!")
            print(f"Ответ сервера: {response.json()}")
            print("\n📱 Проверьте главную страницу: http://localhost:8000")
            print("⚙️ Настройки: http://localhost:8000/settings")
        else:
            print(f"❌ Ошибка при отправке данных: {response.status_code}")
            print(f"Ответ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к серверу.")
        print("Убедитесь, что приложение запущено на http://localhost:8000")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")

if __name__ == "__main__":
    test_webhook()
