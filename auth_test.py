#!/usr/bin/env python3
"""
🔧 ЭКСПРЕСС-ТЕСТ АВТОРИЗАЦИИ ДЛЯ ИГРЫ
Команда MACAN team: Эрмек Озгонбеков, Элдияр Адылбеков, Каныкей Ашыракманова
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

def test_live_game_auth():
    """Тестируем авторизацию для уже идущей игры"""
    
    print("🎮 ЭКСПРЕСС-ТЕСТ ДЛЯ ИГРЫ")
    print("=" * 40)
    print(f"Токен: {TOKEN[:8]}...")
    
    base_url = "https://games.datsteam.dev/api"
    
    # Различные варианты авторизации
    auth_variants = [
        # Query параметры
        ({"token": TOKEN}, {}, "Query: token"),
        ({"api_key": TOKEN}, {}, "Query: api_key"),
        ({"auth": TOKEN}, {}, "Query: auth"),
        
        # Заголовки
        ({}, {"Authorization": f"Bearer {TOKEN}"}, "Header: Bearer"),
        ({}, {"Authorization": TOKEN}, "Header: без Bearer"),
        ({}, {"X-API-Key": TOKEN}, "Header: X-API-Key"),
        ({}, {"Token": TOKEN}, "Header: Token"),
        ({}, {"X-Auth-Token": TOKEN}, "Header: X-Auth-Token"),
        
        # Комбинированные
        ({"token": TOKEN}, {"Authorization": f"Bearer {TOKEN}"}, "Query + Header"),
    ]
    
    headers_base = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    endpoints = ["/arena", "/rounds"]
    
    for params, headers_extra, desc in auth_variants:
        print(f"\n🧪 {desc}:")
        
        headers = {**headers_base, **headers_extra}
        
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                response = requests.get(url, headers=headers, params=params, timeout=5)
                
                print(f"  {endpoint}: {response.status_code}", end="")
                
                if response.status_code == 200:
                    print(" ✅ УСПЕХ!")
                    data = response.json()
                    
                    if endpoint == "/arena":
                        print(f"    Наших муравьев: {len(data.get('ants', []))}")
                        print(f"    До следующего хода: {data.get('nextTurnIn', 0)} сек")
                        print(f"    🎯 НАЙДЕН РАБОЧИЙ ФОРМАТ: {desc}")
                        return params, headers_extra
                    else:
                        print(f"    Раундов: {len(data.get('rounds', []))}")
                        
                elif response.status_code == 400:
                    print(f" ❌ Плохой запрос")
                    if "token" in response.text.lower():
                        print(f"    {response.text[:100]}")
                elif response.status_code == 403:
                    print(f" ❌ Доступ запрещен")
                elif response.status_code == 401:
                    print(f" ❌ Не авторизован")
                else:
                    print(f" ❓ {response.status_code}")
                    
            except Exception as e:
                print(f"  {endpoint}: ❌ {e}")
    
    return None, None

if __name__ == "__main__":
    working_params, working_headers = test_live_game_auth()
    
    if working_params is not None or working_headers:
        print(f"\n🎉 ГОТОВ К ИГРЕ!")
        print(f"Параметры: {working_params}")
        print(f"Заголовки: {working_headers}")
    else:
        print(f"\n❌ НЕ УДАЛОСЬ НАЙТИ РАБОЧИЙ ФОРМАТ")
        print("Возможные причины:")
        print("- Неверный токен")
        print("- Команда не зарегистрирована")
        print("- Игра не идет")
