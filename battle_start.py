#!/usr/bin/env python3
"""
🏆 БОЕВОЙ СТАРТ ДЛЯ ЗАРЕГИСТРИРОВАННОЙ КОМАНДЫ
Команда MACAN team: Эрмек Озгонбеков, Элдияр Адылбеков, Каныкей Ашыракманова

Запуск бота для участия в раунде БЕЗ повторной регистрации
"""

import sys
import time
from config import APIclient, data

def battle_start():
    """Запуск бота для уже зарегистрированной команды"""
    
    # Проверяем аргументы командной строки  
    use_test_server = True
    if len(sys.argv) > 1 and sys.argv[1] == "--prod":
        use_test_server = False
        print("⚔️ ЗАПУСК НА БОЕВОМ СЕРВЕРЕ!")
        print(f"Команда: {data['name']}")
        print("Участники:", ", ".join(data['members']))
        confirm = input("Введите 'YES' для подтверждения: ")
        if confirm != 'YES':
            print("❌ Запуск отменен")
            return False
    
    client = APIclient(use_test_server=use_test_server)
    
    print("🎮 Проверяем состояние арены...")
    
    # Проверяем, можем ли получить данные арены (значит уже зарегистрированы)
    arena_data = client.get_arena()
    if not arena_data:
        print("❌ Не удалось получить данные арены")
        print("Возможные причины:")
        print("1. Раунд еще не начался")
        print("2. Команда не зарегистрирована") 
        print("3. Проблемы с токеном")
        return False
        
    print("✅ Подключение к арене успешно!")
    print(f"🐜 Наших муравьев: {len(arena_data.get('myAnts', []))}")
    print(f"⏰ До следующего хода: {arena_data.get('nextTurnIn', 0):.1f} сек")
    
    # Основной игровой цикл
    turn_count = 0
    try:
        print("🚀 НАЧИНАЕМ БОЕВОЙ РАУНД!")
        print("=" * 50)
        
        while True:
            turn_count += 1
            print(f"\n=== ХОД {turn_count} ===")
            
            # Получаем текущие данные арены
            arena_data = client.get_arena()
            if not arena_data:
                print("❌ Ошибка получения данных арены")
                time.sleep(1)
                continue
                
            # Проверяем, продолжается ли раунд
            next_turn_in = arena_data.get('nextTurnIn', 0)
            if next_turn_in <= 0:
                print("🏁 РАУНД ЗАВЕРШЕН!")
                print(f"Общее количество ходов: {turn_count-1}")
                break
                
            # Выполняем ход
            success = client.execute_turn()
            if not success:
                print("⚠️ Ошибка выполнения хода, продолжаем...")
            
            # Ждем до следующего хода
            sleep_time = max(0.5, next_turn_in - 0.2)  # Небольшой запас
            if sleep_time > 0:
                time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        print(f"\n⏹️ Остановлено пользователем на ходу {turn_count}")
        print("Для возобновления запустите:")
        server_flag = "--prod" if not use_test_server else ""
        print(f"python battle_start.py {server_flag}")
        
    except Exception as e:
        print(f"\n💥 Критическая ошибка на ходу {turn_count}: {e}")
        print("Попробуйте перезапустить бота:")
        server_flag = "--prod" if not use_test_server else ""
        print(f"python battle_start.py {server_flag}")
        import traceback
        traceback.print_exc()
        
    return True

if __name__ == "__main__":
    battle_start()
