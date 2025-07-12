#!/usr/bin/env python3
"""
🔍 ДЕТАЛЬНАЯ ПРОВЕРКА РЕГИСТРАЦИИ
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

def test_registration():
    """Детальный тест регистрации"""
    
    team_data = {
        "name": "MACAN team",
        "members": [
            "Эрмек Озгонбеков",
            "Элдияр Адылбеков", 
            "Каныкей Ашыракманова"
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    base_url = "https://games.datsteam.dev/api"
    
    print("🔍 ДЕТАЛЬНАЯ ПРОВЕРКА РЕГИСТРАЦИИ")
    print("=" * 50)
    print(f"Команда: {team_data['name']}")
    print(f"Участники: {team_data['members']}")
    print(f"Токен: {TOKEN[:8]}...")
    print("=" * 50)
    
    try:
        url = f"{base_url}/register"
        params = {"token": TOKEN}
        
        print(f"URL: {url}")
        print(f"Параметры: {params}")
        print(f"Данные: {team_data}")
        
        response = requests.post(url, headers=headers, json=team_data, params=params, timeout=10)
        
        print(f"\nОтвет сервера:")
        print(f"Статус: {response.status_code}")
        print(f"Заголовки ответа: {dict(response.headers)}")
        print(f"Тело ответа: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ РЕГИСТРАЦИЯ УСПЕШНА!")
            return True
        elif response.status_code == 409:
            print("✅ УЖЕ ЗАРЕГИСТРИРОВАНЫ!")
            return True
        else:
            print("❌ ОШИБКА РЕГИСТРАЦИИ")
            return False
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False

def test_arena_access():
    """Тест доступа к арене после регистрации"""
    
    base_url = "https://games.datsteam.dev/api"
    params = {"token": TOKEN}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("\n🏟️ ПРОВЕРКА ДОСТУПА К АРЕНЕ")
    print("=" * 50)
    
    try:
        url = f"{base_url}/arena"
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"URL: {url}")
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ ДОСТУП К АРЕНЕ ПОЛУЧЕН!")
            print(f"Наших муравьев: {len(data.get('ants', []))}")
            print(f"До следующего хода: {data.get('nextTurnIn', 0)} сек")
            return True
        else:
            print("❌ НЕТ ДОСТУПА К АРЕНЕ")
            return False
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False

if __name__ == "__main__":
    registration_ok = test_registration()
    if registration_ok:
        arena_ok = test_arena_access()
        if arena_ok:
            print("\n🎉 ВСЕ ГОТОВО ДЛЯ ИГРЫ!")
        else:
            print("\n⏳ ДОЖДИТЕСЬ НАЧАЛА РАУНДА")
    else:
        print("\n❌ ПРОБЛЕМЫ С РЕГИСТРАЦИЕЙ")
