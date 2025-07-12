"""
Проверка готовности к боевым раундам
"""
import os
import sys
from config import APIclient, data
import requests

def check_env_file():
    """Проверка .env файла"""
    print("📄 Проверка .env файла...")
    
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        print("   Создайте файл .env с содержимым:")
        print("   TOKEN=ваш_токен_здесь")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
    
    if 'TOKEN=' not in content:
        print("❌ Токен не найден в .env!")
        return False
    
    token_line = [line for line in content.split('\n') if line.startswith('TOKEN=')]
    if token_line:
        token = token_line[0].split('=', 1)[1].strip()
        if len(token) < 10:
            print("❌ Токен слишком короткий!")
            return False
        print(f"✅ Токен найден: {token[:10]}...")
        return True
    
    return False

def check_team_data():
    """Проверка данных команды"""
    print("\n👥 Проверка данных команды...")
    
    print(f"   Название: {data['name']}")
    print(f"   Участники:")
    for i, member in enumerate(data['members'], 1):
        print(f"     {i}. {member}")
    
    if data['name'] == "MACAN team" and len(data['members']) == 3:
        print("✅ Данные команды корректны")
        return True
    else:
        print("❌ Проверьте данные команды в config.py")
        return False

def check_dependencies():
    """Проверка зависимостей"""
    print("\n📦 Проверка зависимостей...")
    
    required = ['requests', 'python-dotenv']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Установите недостающие пакеты:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    print("✅ Все зависимости установлены")
    return True

def check_api_connection():
    """Проверка соединения с серверами"""
    print("\n🌐 Проверка соединения с серверами...")
    
    # Тестовый сервер
    try:
        test_client = APIclient(use_test_server=True)
        rounds_info = test_client.get_rounds_info()
        if rounds_info:
            print("   ✅ Тестовый сервер доступен")
            test_ok = True
        else:
            print("   ❌ Тестовый сервер недоступен")
            test_ok = False
    except Exception as e:
        print(f"   ❌ Ошибка тестового сервера: {e}")
        test_ok = False
    
    # Боевой сервер
    try:
        prod_client = APIclient(use_test_server=False)
        rounds_info = prod_client.get_rounds_info()
        if rounds_info:
            print("   ✅ Боевой сервер доступен")
            prod_ok = True
        else:
            print("   ❌ Боевой сервер недоступен")
            prod_ok = False
    except Exception as e:
        print(f"   ❌ Ошибка боевого сервера: {e}")
        prod_ok = False
    
    return test_ok and prod_ok

def check_file_structure():
    """Проверка структуры файлов"""
    print("\n📁 Проверка структуры файлов...")
    
    required_files = [
        'config.py',
        'strategy.py', 
        'main.py',
        'training.py',
        'api_test.py',
        'requirements.txt',
        '.env'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False
    
    print("✅ Все файлы на месте")
    return True

def test_registration():
    """Тест регистрации на тестовом сервере"""
    print("\n📝 Тест регистрации на тестовом сервере...")
    
    try:
        client = APIclient(use_test_server=True)
        result = client.register_for_round()
        
        if result:
            print("✅ Регистрация на тестовом сервере работает")
            return True
        else:
            print("❌ Регистрация не удалась")
            return False
    except Exception as e:
        print(f"❌ Ошибка регистрации: {e}")
        return False

def main():
    """Основная проверка готовности"""
    print("🏆 ПРОВЕРКА ГОТОВНОСТИ К БОЕВЫМ РАУНДАМ")
    print("Команда: MACAN team")
    print("=" * 50)
    
    checks = [
        ("Структура файлов", check_file_structure),
        ("Файл .env", check_env_file),
        ("Данные команды", check_team_data),
        ("Зависимости", check_dependencies),
        ("Соединение с API", check_api_connection),
        ("Тест регистрации", test_registration)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ Ошибка в проверке '{check_name}': {e}")
            results[check_name] = False
    
    # Итоговый отчет
    print("\n" + "=" * 50)
    print("📊 ИТОГОВЫЙ ОТЧЕТ:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ ПРОЙДЕНА" if result else "❌ НЕ ПРОЙДЕНА"
        print(f"{check_name}: {status}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\n🎯 Готовность: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("\n🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("🚀 КОМАНДА ГОТОВА К БОЕВЫМ РАУНДАМ!")
        print("\nДля запуска в боевом режиме:")
        print("   python config.py --prod")
        
    elif success_rate >= 80:
        print("\n⚠️ Есть незначительные проблемы, но можно участвовать")
        print("Рекомендуется исправить выявленные проблемы")
        
    else:
        print("\n🚨 КРИТИЧЕСКИЕ ПРОБЛЕМЫ!")
        print("Необходимо исправить ошибки перед участием в боевых раундах")
        
    print(f"\n📚 Для получения помощи смотрите:")
    print(f"   BATTLE_GUIDE.md - Подробное руководство")
    print(f"   README.md - Общая документация")

if __name__ == "__main__":
    main()
    
    input("\nНажмите Enter для выхода...")
