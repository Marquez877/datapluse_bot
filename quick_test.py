#!/usr/bin/env python3
"""
🔧 БЫСТРЫЙ ТЕСТ QUERY ПАРАМЕТРОВ
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

def test_query_params():
    """Тестируем разные названия query параметров"""
    
    base_url = "https://games.datsteam.dev/api"
    
    param_names = [
        "token",
        "api_key", 
        "apikey",
        "auth",
        "key",
        "access_token",
        "bearer",
        "authorization"
    ]
    
    for param_name in param_names:
        print(f"🧪 Тестируем параметр: {param_name}")
        
        try:
            params = {param_name: TOKEN}
            response = requests.get(f"{base_url}/rounds", params=params, timeout=5)
            
            print(f"  Статус: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ УСПЕХ с параметром '{param_name}'!")
                print(f"  URL: {response.url}")
                return param_name
            else:
                print(f"  Ответ: {response.text[:100]}...")
                
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
    
    return None

if __name__ == "__main__":
    working_param = test_query_params()
    if working_param:
        print(f"\n🎉 Рабочий параметр: {working_param}")
    else:
        print("\n❌ Ни один параметр не работает")
