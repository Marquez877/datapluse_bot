"""
Быстрый тест подключения к API DatsPulse
"""
from config import APIclient
import time

def quick_api_test():
    """Быстрая проверка API соединения"""
    print("🔌 БЫСТРЫЙ ТЕСТ API DATSPULSE")
    print("=" * 40)
    
    # Тест тестового сервера
    print("\n🧪 Тестирование ТЕСТОВОГО сервера...")
    test_client = APIclient(use_test_server=True)
    
    try:
        # Тест получения раундов
        rounds_info = test_client.get_rounds_info()
        if rounds_info:
            print("✅ Тестовый сервер: Соединение OK")
            print(f"📊 Данные получены: {type(rounds_info)}")
        else:
            print("❌ Тестовый сервер: Нет ответа")
            
        # Тест получения арены (может быть ошибка если не зарегистрированы)
        arena_data = test_client.get_arena()
        if arena_data:
            print("✅ Тестовый сервер: Данные арены получены")
            print(f"🎮 Найдено муравьев: {len(arena_data.get('ants', []))}")
            print(f"👹 Найдено врагов: {len(arena_data.get('enemies', []))}")
            print(f"🍎 Найдено ресурсов: {len(arena_data.get('food', []))}")
            print(f"🏆 Текущий счет: {arena_data.get('score', 0)}")
        else:
            print("⚠️ Тестовый сервер: Нет данных арены (возможно, нужна регистрация)")
            
    except Exception as e:
        print(f"❌ Ошибка тестового сервера: {e}")
    
    # Тест боевого сервера
    print("\n⚔️ Тестирование БОЕВОГО сервера...")
    prod_client = APIclient(use_test_server=False)
    
    try:
        rounds_info = prod_client.get_rounds_info()
        if rounds_info:
            print("✅ Боевой сервер: Соединение OK")
        else:
            print("❌ Боевой сервер: Нет ответа")
            
    except Exception as e:
        print(f"❌ Ошибка боевого сервера: {e}")
    
    print("\n" + "=" * 40)
    print("✅ Тест завершен!")
    print("\nДля полного тестирования запустите:")
    print("python training.py")

def test_registration():
    """Тест регистрации на раунд"""
    print("\n📝 ТЕСТ РЕГИСТРАЦИИ НА РАУНД")
    print("=" * 40)
    
    client = APIclient(use_test_server=True)  # Используем тестовый сервер
    
    try:
        result = client.register_for_round()
        if result:
            print("✅ Регистрация успешна!")
            print(f"📋 Ответ сервера:")
            print(f"   {result}")
            
            # Проверяем данные арены после регистрации
            time.sleep(1)
            arena_data = client.get_arena()
            if arena_data:
                print(f"\n🎮 Данные арены после регистрации:")
                print(f"   Муравьев: {len(arena_data.get('ants', []))}")
                print(f"   Ход номер: {arena_data.get('turnNo', 'N/A')}")
                print(f"   До следующего хода: {arena_data.get('nextTurnIn', 0)} сек")
                print(f"   Дом: {arena_data.get('home', [])}")
            else:
                print("⚠️ Данные арены недоступны")
                
        else:
            print("❌ Регистрация не удалась")
            
    except Exception as e:
        print(f"❌ Ошибка регистрации: {e}")

def show_api_info():
    """Показать информацию об API"""
    print("\n📖 ИНФОРМАЦИЯ О API")
    print("=" * 40)
    print("🌐 Тестовый сервер: https://games-test.datsteam.dev/api")
    print("🌐 Боевой сервер: https://games.datsteam.dev/api")
    print("📚 Документация: https://games.datsteam.dev/static/datspulse/openapi/#/")
    print("\n📋 Доступные endpoints:")
    print("   GET  /api/arena     - Состояние арены")
    print("   POST /api/move      - Отправка команд")
    print("   POST /api/register  - Регистрация на раунд")
    print("   GET  /api/logs      - Журнал действий")
    print("   GET  /api/rounds    - Информация о раундах")
    print("\n⚡ Лимит: 3 запроса в секунду")
    print("🔑 Требуется токен в заголовке Authorization")

if __name__ == "__main__":
    while True:
        print("\n" + "🎯 МЕНЮ ТЕСТИРОВАНИЯ API")
        print("=" * 30)
        print("1. Быстрый тест соединения")
        print("2. Тест регистрации на раунд")
        print("3. Информация об API")
        print("4. Полное тестирование (training.py)")
        print("5. Выход")
        
        choice = input("\nВыберите опцию (1-5): ").strip()
        
        if choice == '1':
            quick_api_test()
        elif choice == '2':
            test_registration()
        elif choice == '3':
            show_api_info()
        elif choice == '4':
            import subprocess
            import sys
            try:
                subprocess.run([sys.executable, "training.py"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Ошибка запуска training.py: {e}")
            except FileNotFoundError:
                print("Файл training.py не найден")
        elif choice == '5':
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор")
