#!/usr/bin/env python3
"""
🔍 ТЕСТИРОВАНИЕ РАЗНЫХ ФОРМАТОВ ТОКЕНА И API
Команда MACAN team: Эрмек Озгонбеков, Элдияр Адылбеков, Каныкей Ашыракманова
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

def test_token_formats():
    """Тестируем разные форматы токена и заголовков"""
    
    print("🔍 ТЕСТИРОВАНИЕ ФОРМАТОВ ТОКЕНА")
    print("=" * 50)
    print(f"Токен: {TOKEN}")
    print("=" * 50)
    
    # Различные базовые URL для тестирования
    base_urls = [
        "https://games.datsteam.dev/api",
        "https://games-test.datsteam.dev/api", 
        "https://games.datsteam.dev",
        "https://games-test.datsteam.dev"
    ]
    
    # Различные форматы заголовков авторизации
    header_formats = [
        {"Authorization": f"Bearer {TOKEN}"},
        {"Authorization": f"{TOKEN}"},
        {"X-API-Key": TOKEN},
        {"Token": TOKEN},
        {"API-Token": TOKEN},
        {"X-Token": TOKEN}
    ]
    
    # Тестируем каждую комбинацию
    for base_url in base_urls:
        print(f"\n🌐 Тестируем сервер: {base_url}")
        print("-" * 40)
        
        for i, headers in enumerate(header_formats):
            print(f"\nФормат {i+1}: {headers}")
            
            # Добавляем стандартные заголовки
            full_headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                **headers
            }
            
            # Тестируем разные эндпоинты
            endpoints = ["/rounds", "/arena", "/register"]
            
            for endpoint in endpoints:
                try:
                    url = f"{base_url}{endpoint}"
                    response = requests.get(url, headers=full_headers, timeout=5)
                    
                    print(f"  {endpoint}: {response.status_code}", end="")
                    
                    if response.status_code == 200:
                        print(" ✅ УСПЕХ!")
                        print(f"    Ответ: {response.text[:100]}...")
                        return base_url, headers, endpoint
                    elif response.status_code == 401:
                        print(" ❌ Неавторизован")
                    elif response.status_code == 403:
                        print(" ❌ Доступ запрещен")
                    elif response.status_code == 404:
                        print(" ❌ Не найден")
                    elif response.status_code == 400:
                        print(" ❌ Плохой запрос")
                        if "token" in response.text.lower():
                            print(f"    Ошибка токена: {response.text}")
                    else:
                        print(f" ❓ Код {response.status_code}")
                        
                except Exception as e:
                    print(f"  {endpoint}: ❌ Ошибка - {e}")
    
    return None, None, None

def test_specific_documentation_format():
    """Тестируем специфический формат из документации"""
    
    print("\n🔧 ТЕСТИРОВАНИЕ ПО ДОКУМЕНТАЦИИ")
    print("=" * 50)
    
    # Попробуем вариант без Bearer
    headers_no_bearer = {
        "Authorization": TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Попробуем с X-API-Key
    headers_api_key = {
        "X-API-Key": TOKEN,
        "Content-Type": "application/json", 
        "Accept": "application/json"
    }
    
    # Попробуем query parameter
    test_cases = [
        ("Authorization header без Bearer", "https://games.datsteam.dev/api/rounds", headers_no_bearer, {}),
        ("X-API-Key header", "https://games.datsteam.dev/api/rounds", headers_api_key, {}),
        ("Query parameter", "https://games.datsteam.dev/api/rounds", {}, {"token": TOKEN}),
        ("Query parameter alt", "https://games.datsteam.dev/api/rounds", {}, {"api_key": TOKEN}),
    ]
    
    for name, url, headers, params in test_cases:
        print(f"\n🧪 {name}:")
        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            print(f"  Статус: {response.status_code}")
            print(f"  Ответ: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("  ✅ УСПЕХ! Этот формат работает!")
                return headers, params
                
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
    
    return None, None

def test_post_requests():
    """Тестируем POST запросы с разными форматами"""
    
    print("\n📤 ТЕСТИРОВАНИЕ POST ЗАПРОСОВ")
    print("=" * 50)
    
    # Данные для регистрации
    team_data = {
        "name": "MACAN team",
        "members": [
            "Эрмек Озгонбеков",
            "Элдияр Адылбеков", 
            "Каныкей Ашыракманова"
        ]
    }
    
    # Тестируем разные форматы для POST
    header_formats = [
        {"Authorization": f"Bearer {TOKEN}"},
        {"Authorization": f"{TOKEN}"},
        {"X-API-Key": TOKEN},
    ]
    
    base_urls = [
        "https://games.datsteam.dev/api",
        "https://games-test.datsteam.dev/api"
    ]
    
    for base_url in base_urls:
        print(f"\n🌐 Сервер: {base_url}")
        
        for i, auth_headers in enumerate(header_formats):
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                **auth_headers
            }
            
            print(f"\nФормат {i+1}: {auth_headers}")
            
            try:
                url = f"{base_url}/register"
                response = requests.post(url, headers=headers, json=team_data, timeout=10)
                
                print(f"  /register: {response.status_code}")
                print(f"  Ответ: {response.text[:200]}...")
                
                if response.status_code in [200, 201]:
                    print("  ✅ РЕГИСТРАЦИЯ УСПЕШНА!")
                    return True
                elif response.status_code == 409:
                    print("  ✅ УЖЕ ЗАРЕГИСТРИРОВАНЫ!")
                    return True
                    
            except Exception as e:
                print(f"  ❌ Ошибка: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 ПОЛНОЕ ТЕСТИРОВАНИЕ API И ТОКЕНА")
    print("=" * 60)
    
    # Тест 1: Разные форматы токена
    working_url, working_headers, working_endpoint = test_token_formats()
    
    if working_url:
        print(f"\n🎉 НАЙДЕН РАБОЧИЙ ФОРМАТ!")
        print(f"URL: {working_url}")
        print(f"Заголовки: {working_headers}")
        print(f"Эндпоинт: {working_endpoint}")
    
    # Тест 2: Специфические форматы из документации
    doc_headers, doc_params = test_specific_documentation_format()
    
    # Тест 3: POST запросы
    print("\n" + "=" * 60)
    post_success = test_post_requests()
    
    print("\n🏁 ИТОГОВЫЙ ОТЧЕТ:")
    print("=" * 60)
    if working_url or doc_headers or post_success:
        print("✅ Найден рабочий формат API!")
    else:
        print("❌ Ни один формат не работает")
        print("Возможные проблемы:")
        print("- Неверный токен")
        print("- Сервер недоступен") 
        print("- Неизвестный формат авторизации")
