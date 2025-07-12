"""
Тестирование API и тренировка перед боевыми раундами
Команда MACAN team:
- Эрмек Озгонбеков
- Элдияр Адылбеков
- Каныкей Ашыракманова
"""
import time
from config import APIclient

class TrainingSession:
    """Класс для тренировочных сессий"""
    
    def __init__(self, use_test_server=True):
        self.client = APIclient(use_test_server=use_test_server)
        print(f"🌐 Подключение к {'ТЕСТОВОМУ' if use_test_server else 'БОЕВОМУ'} серверу")
    
    def test_connection(self):
        """Тестирование базового соединения"""
        print("\n🔌 Тестирование соединения...")
        
        try:
            # Тест получения информации о раундах
            rounds_info = self.client.get_rounds_info()
            if rounds_info:
                print("✅ Соединение с API успешно!")
                print(f"📊 Информация о раундах получена")
                return True
            else:
                print("❌ Не удалось получить информацию о раундах")
                return False
        except Exception as e:
            print(f"❌ Ошибка соединения: {e}")
            return False
    
    def test_registration(self):
        """Тестирование регистрации на раунд"""
        print("\n📝 Тестирование регистрации...")
        
        try:
            result = self.client.register_for_round()
            if result:
                print("✅ Регистрация прошла успешно!")
                print(f"📋 Ответ сервера: {result}")
                return True
            else:
                print("❌ Регистрация не удалась")
                return False
        except Exception as e:
            print(f"❌ Ошибка регистрации: {e}")
            return False
    
    def test_arena_data(self):
        """Тестирование получения данных арены"""
        print("\n🏟️ Тестирование получения данных арены...")
        
        try:
            arena_data = self.client.get_arena()
            if arena_data:
                print("✅ Данные арены получены!")
                print(f"🐜 Муравьев: {len(arena_data.get('ants', []))}")
                print(f"👹 Врагов: {len(arena_data.get('enemies', []))}")
                print(f"🍎 Ресурсов: {len(arena_data.get('food', []))}")
                print(f"🏠 Координаты дома: {arena_data.get('home', [])}")
                print(f"🏆 Счет: {arena_data.get('score', 0)}")
                print(f"🔢 Номер хода: {arena_data.get('turnNo', 'N/A')}")
                print(f"⏰ До следующего хода: {arena_data.get('nextTurnIn', 0)} сек")
                return arena_data
            else:
                print("❌ Не удалось получить данные арены")
                return None
        except Exception as e:
            print(f"❌ Ошибка получения данных арены: {e}")
            return None
    
    def test_move_command(self, arena_data):
        """Тестирование отправки команд движения"""
        print("\n🚶 Тестирование отправки команд...")
        
        if not arena_data:
            print("❌ Нет данных арены для тестирования")
            return False
        
        ants = arena_data.get('ants', [])
        if not ants:
            print("❌ Нет муравьев для тестирования движения")
            return False
        
        # Берем первого муравья и даем ему простую команду
        test_ant = ants[0]
        print(f"🐜 Тестируем движение муравья {test_ant['id'][:8]}...")
        
        # Простое движение на соседний гекс
        neighbors = self.client.get_neighbors(test_ant['q'], test_ant['r'])
        if neighbors:
            target = neighbors[0]
            test_moves = [{
                "ant": test_ant['id'],
                "path": [{"q": target[0], "r": target[1]}]
            }]
            
            try:
                result = self.client.send_move(test_moves)
                if result is not None:
                    print("✅ Команда движения отправлена успешно!")
                    print(f"📋 Ответ сервера: {result}")
                    return True
                else:
                    print("❌ Ошибка отправки команды")
                    return False
            except Exception as e:
                print(f"❌ Ошибка отправки команды: {e}")
                return False
        else:
            print("❌ Нет доступных соседних гексов")
            return False
    
    def test_game_logs(self):
        """Тестирование получения логов"""
        print("\n📜 Тестирование получения логов...")
        
        try:
            logs = self.client.get_logs()
            if logs:
                print("✅ Логи получены успешно!")
                print(f"📊 Количество записей в логах: {len(logs) if isinstance(logs, list) else 'N/A'}")
                return True
            else:
                print("❌ Не удалось получить логи")
                return False
        except Exception as e:
            print(f"❌ Ошибка получения логов: {e}")
            return False
    
    def run_full_test(self):
        """Полное тестирование всех функций API"""
        print("🚀 Запуск полного тестирования API...")
        print("=" * 60)
        
        test_results = {
            'connection': False,
            'registration': False,
            'arena_data': False,
            'move_command': False,
            'logs': False
        }
        
        # 1. Тест соединения
        test_results['connection'] = self.test_connection()
        
        # 2. Тест регистрации
        if test_results['connection']:
            test_results['registration'] = self.test_registration()
        
        # 3. Тест получения данных арены
        arena_data = None
        if test_results['registration']:
            arena_data = self.test_arena_data()
            test_results['arena_data'] = arena_data is not None
        
        # 4. Тест команд движения
        if test_results['arena_data'] and arena_data:
            test_results['move_command'] = self.test_move_command(arena_data)
        
        # 5. Тест логов
        test_results['logs'] = self.test_game_logs()
        
        # Итоговый отчет
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ:")
        print("=" * 60)
        
        for test_name, result in test_results.items():
            status = "✅ ПРОЙДЕН" if result else "❌ НЕ ПРОЙДЕН"
            test_name_ru = {
                'connection': 'Соединение с API',
                'registration': 'Регистрация на раунд',
                'arena_data': 'Получение данных арены',
                'move_command': 'Отправка команд движения',
                'logs': 'Получение логов'
            }.get(test_name, test_name)
            
            print(f"{test_name_ru}: {status}")
        
        success_rate = sum(test_results.values()) / len(test_results) * 100
        print(f"\n🎯 Успешность тестирования: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 Система готова к боевым раундам!")
        elif success_rate >= 60:
            print("⚠️ Есть проблемы, но основные функции работают")
        else:
            print("🚨 Критические проблемы! Необходимо исправление")
        
        return test_results
    
    def run_training_round(self, max_turns=5):
        """Запуск тренировочного раунда"""
        print(f"🏃 Запуск тренировочного раунда (максимум {max_turns} ходов)...")
        
        # Регистрируемся
        if not self.test_registration():
            return False
        
        turn_count = 0
        successful_turns = 0
        
        try:
            while turn_count < max_turns:
                print(f"\n--- Тренировочный ход {turn_count + 1} ---")
                
                # Выполняем ход
                success = self.client.execute_turn()
                if success:
                    successful_turns += 1
                    print(f"✅ Ход {turn_count + 1} выполнен успешно")
                else:
                    print(f"❌ Ошибка в ходе {turn_count + 1}")
                
                turn_count += 1
                
                # Ждем между ходами
                time.sleep(3)
                
        except KeyboardInterrupt:
            print("\n⏹️ Тренировка прервана пользователем")
        except Exception as e:
            print(f"\n❌ Ошибка в тренировочном раунде: {e}")
        
        # Статистика тренировки
        print(f"\n📊 СТАТИСТИКА ТРЕНИРОВКИ:")
        print(f"Всего ходов: {turn_count}")
        print(f"Успешных ходов: {successful_turns}")
        print(f"Успешность: {successful_turns/turn_count*100:.1f}%" if turn_count > 0 else "N/A")
        
        return successful_turns == turn_count

def main():
    """Главное меню тренировки"""
    while True:
        print("\n" + "="*50)
        print("🎯 МЕНЮ ТРЕНИРОВКИ DATSPULSE BOT")
        print("="*50)
        print("1. Полное тестирование API (рекомендуется)")
        print("2. Тест соединения")
        print("3. Тренировочный раунд (тестовый сервер)")
        print("4. Боевой режим (боевой сервер)")
        print("5. Выход")
        
        choice = input("\nВыберите опцию (1-5): ").strip()
        
        if choice == '1':
            trainer = TrainingSession(use_test_server=True)
            trainer.run_full_test()
            
        elif choice == '2':
            use_test = input("Использовать тестовый сервер? (y/n): ").lower().strip() == 'y'
            trainer = TrainingSession(use_test_server=use_test)
            trainer.test_connection()
            
        elif choice == '3':
            max_turns = input("Максимум ходов для тренировки (по умолчанию 5): ").strip()
            max_turns = int(max_turns) if max_turns.isdigit() else 5
            
            trainer = TrainingSession(use_test_server=True)
            trainer.run_training_round(max_turns)
            
        elif choice == '4':
            confirm = input("⚠️ Вы уверены, что хотите запустить БОЕВОЙ режим? (yes/no): ").strip().lower()
            if confirm == 'yes':
                from main import GameBot
                bot = GameBot()
                # Переключаем на боевой сервер
                bot.api_client.base_url = "https://games.datsteam.dev/api"
                bot.run_game_loop()
            else:
                print("Боевой режим отменен")
                
        elif choice == '5':
            print("👋 До свидания! Удачи в соревновании!")
            break
            
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main()
