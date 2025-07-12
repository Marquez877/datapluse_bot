#!/usr/bin/env python3
"""
🔍 ПРОВЕРКА СТАТУСА РАУНДА
Команда MACAN team: Эрмек Озгонбеков, Элдияр Адылбеков, Каныкей Ашыракманова
"""

import requests
from config import TOKEN, HEADERS, BASE_URL_PROD, BASE_URL_TEST

def check_round_status():
    """Проверяем статус раундов на боевом сервере"""
    
    print("🔍 ПРОВЕРКА СТАТУСА РАУНДОВ")
    print("=" * 40)
    
    # Проверяем боевой сервер
    print("⚔️ Проверяем БОЕВОЙ сервер...")
    try:
        url = f"{BASE_URL_PROD}/rounds"
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Боевой сервер доступен")
            print(f"Данные: {data}")
        else:
            print(f"❌ Ошибка боевого сервера: {response.status_code}")
            print(f"Текст ошибки: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка соединения с боевым сервером: {e}")
    
    print("\n" + "=" * 40)
    
    # Проверяем тестовый сервер для сравнения
    print("🧪 Проверяем ТЕСТОВЫЙ сервер...")
    try:
        url = f"{BASE_URL_TEST}/rounds"
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Тестовый сервер доступен")
            print(f"Данные: {data}")
        else:
            print(f"❌ Ошибка тестового сервера: {response.status_code}")
            print(f"Текст ошибки: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка соединения с тестовым сервером: {e}")

def check_arena_access():
    """Проверяем доступ к арене"""
    
    print("\n🏟️ ПРОВЕРКА ДОСТУПА К АРЕНЕ")
    print("=" * 40)
    
    # Проверяем боевую арену
    print("⚔️ Проверяем боевую арену...")
    try:
        url = f"{BASE_URL_PROD}/arena"
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Доступ к боевой арене получен!")
            print(f"Наших муравьев: {len(data.get('myAnts', []))}")
            print(f"До следующего хода: {data.get('nextTurnIn', 0)} сек")
            return True
        elif response.status_code == 403:
            print("❌ Доступ запрещен (403 Forbidden)")
            print("Возможные причины:")
            print("- Команда не зарегистрирована на текущий раунд")
            print("- Раунд еще не начался")
            print("- Раунд уже закончился")
            print("- Неверный токен")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"Текст ошибки: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")
    
    return False

if __name__ == "__main__":
    print(f"🔑 Используется токен: {TOKEN[:8]}...")
    check_round_status()
    arena_available = check_arena_access()
    
    if arena_available:
        print("\n🎮 ГОТОВ К ИГРЕ!")
        print("Запустите: python battle_start.py --prod")
    else:
        print("\n⏳ НЕ ГОТОВ К ИГРЕ")
        print("Дождитесь начала раунда или проверьте регистрацию")
