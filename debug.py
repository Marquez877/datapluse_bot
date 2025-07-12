"""
Утилиты для отладки и анализа игры
Команда MACAN team:
- Эрмек Озгонбеков  
- Элдияр Адылбеков
- Каныкей Ашыракманова
"""
import json
import time
from datetime import datetime
from config import APIclient

class GameAnalyzer:
    """Анализатор игровых данных для отладки"""
    
    def __init__(self):
        self.game_log = []
        self.turn_data = {}
        
    def log_turn(self, turn_number: int, arena_data: dict, moves: list, strategy: str):
        """Логирование данных хода"""
        turn_info = {
            'turn': turn_number,
            'timestamp': datetime.now().isoformat(),
            'strategy': strategy,
            'score': arena_data.get('score', 0),
            'ants_count': len(arena_data.get('ants', [])),
            'enemies_count': len(arena_data.get('enemies', [])),
            'food_count': len(arena_data.get('food', [])),
            'moves_sent': len(moves),
            'next_turn_in': arena_data.get('nextTurnIn', 0)
        }
        
        self.game_log.append(turn_info)
        self.turn_data[turn_number] = {
            'arena': arena_data,
            'moves': moves,
            'info': turn_info
        }
    
    def save_game_log(self, filename: str = None):
        """Сохранение лога игры в файл"""
        if filename is None:
            filename = f"game_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.game_log, f, indent=2, ensure_ascii=False)
            
        print(f"Лог игры сохранен в {filename}")
    
    def print_statistics(self):
        """Вывод статистики игры"""
        if not self.game_log:
            print("Нет данных для анализа")
            return
            
        print("\n" + "="*60)
        print("СТАТИСТИКА ИГРЫ")
        print("="*60)
        
        total_turns = len(self.game_log)
        final_score = self.game_log[-1]['score'] if self.game_log else 0
        max_ants = max(turn['ants_count'] for turn in self.game_log)
        total_moves = sum(turn['moves_sent'] for turn in self.game_log)
        
        print(f"Всего ходов: {total_turns}")
        print(f"Финальный счет: {final_score}")
        print(f"Максимум муравьев: {max_ants}")
        print(f"Всего команд отправлено: {total_moves}")
        
        # Анализ стратегий
        strategies = {}
        for turn in self.game_log:
            strategy = turn['strategy']
            strategies[strategy] = strategies.get(strategy, 0) + 1
            
        print(f"\nИспользованные стратегии:")
        for strategy, count in strategies.items():
            percentage = (count / total_turns) * 100
            print(f"  {strategy}: {count} ходов ({percentage:.1f}%)")
        
        # Динамика счета
        if total_turns > 1:
            score_growth = final_score - self.game_log[0]['score']
            avg_growth = score_growth / total_turns if total_turns > 0 else 0
            print(f"\nРост счета: {score_growth} (+{avg_growth:.2f} за ход)")
        
        print("="*60)

class DebugClient(APIclient):
    """Отладочная версия API клиента с дополнительными возможностями"""
    
    def __init__(self, debug_mode: bool = True):
        super().__init__()
        self.debug_mode = debug_mode
        self.analyzer = GameAnalyzer()
        
    def get_arena_debug(self):
        """Получение данных арены с отладочной информацией"""
        data = self.get_arena()
        if data and self.debug_mode:
            print(f"\n🔍 ОТЛАДКА - Ход {data.get('turnNo', 'N/A')}")
            print(f"⏰ До следующего хода: {data.get('nextTurnIn', 0):.1f}с")
            print(f"🏆 Счет: {data.get('score', 0)}")
            print(f"🐜 Наших муравьев: {len(data.get('ants', []))}")
            print(f"👹 Врагов видно: {len(data.get('enemies', []))}")
            print(f"🍎 Ресурсов видно: {len(data.get('food', []))}")
            print(f"🗺️  Гексов на карте: {len(data.get('map', []))}")
            
            # Детали по муравьям
            ants = data.get('ants', [])
            ant_types = {0: 'Рабочий', 1: 'Боец', 2: 'Разведчик'}
            type_counts = {}
            for ant in ants:
                ant_type = ant_types.get(ant['type'], 'Неизвестный')
                type_counts[ant_type] = type_counts.get(ant_type, 0) + 1
                
            print("📊 Состав армии:")
            for ant_type, count in type_counts.items():
                print(f"   {ant_type}: {count}")
                
        return data
    
    def send_move_debug(self, moves, strategy: str = "unknown"):
        """Отправка команд с отладочной информацией"""
        if self.debug_mode:
            print(f"\n📤 Отправка {len(moves)} команд ({strategy} стратегия)")
            for i, move in enumerate(moves[:3]):  # Показываем первые 3 команды
                ant_id = move['ant'][:8] + "..." if len(move['ant']) > 8 else move['ant']
                path_length = len(move['path'])
                print(f"   {i+1}. Муравей {ant_id}: путь из {path_length} шагов")
            if len(moves) > 3:
                print(f"   ... и еще {len(moves) - 3} команд")
                
        result = self.send_move(moves)
        
        # Логируем данные хода
        if hasattr(self, 'current_arena_data'):
            turn_number = self.current_arena_data.get('turnNo', 0)
            self.analyzer.log_turn(turn_number, self.current_arena_data, moves, strategy)
            
        return result
    
    def run_debug_session(self, max_turns: int = 10):
        """Запуск отладочной сессии с ограниченным количеством ходов"""
        print(f"🚀 Запуск отладочной сессии (максимум {max_turns} ходов)")
        
        turn_count = 0
        try:
            while turn_count < max_turns:
                arena_data = self.get_arena_debug()
                if not arena_data:
                    print("❌ Нет данных арены")
                    break
                
                self.current_arena_data = arena_data
                next_turn_in = arena_data.get('nextTurnIn', 0)
                
                if next_turn_in <= 0:
                    print("🏁 Раунд завершен")
                    break
                
                # Простая логика для отладки
                moves = []
                ants = arena_data.get('ants', [])
                
                for ant in ants:
                    # Случайное движение для тестирования
                    neighbors = self.get_neighbors(ant['q'], ant['r'])
                    if neighbors:
                        target = neighbors[0]  # Берем первого соседа
                        moves.append({
                            "ant": ant['id'],
                            "path": [{'q': target[0], 'r': target[1]}]
                        })
                
                self.send_move_debug(moves, "debug")
                turn_count += 1
                
                print(f"✅ Ход {turn_count} завершен")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n⏹️  Отладочная сессия прервана пользователем")
        except Exception as e:
            print(f"❌ Ошибка в отладочной сессии: {e}")
        
        # Выводим статистику
        self.analyzer.print_statistics()
        
        # Сохраняем лог
        save_log = input("\nСохранить лог игры? (y/n): ").lower().strip()
        if save_log == 'y':
            self.analyzer.save_game_log()

def test_api_connection():
    """Тестирование соединения с API"""
    print("🔌 Тестирование соединения с API...")
    
    client = DebugClient(debug_mode=True)
    
    try:
        # Тест получения данных арены
        arena_data = client.get_arena()
        if arena_data:
            print("✅ Соединение с API успешно!")
            print(f"📊 Получены данные: {len(arena_data)} полей")
            return True
        else:
            print("❌ Не удалось получить данные арены")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")
        return False

if __name__ == "__main__":
    # Меню отладки
    while True:
        print("\n" + "="*50)
        print("ОТЛАДОЧНОЕ МЕНЮ")
        print("="*50)
        print("1. Тест соединения с API")
        print("2. Запуск отладочной сессии")
        print("3. Выход")
        
        choice = input("\nВыберите опцию (1-3): ").strip()
        
        if choice == '1':
            test_api_connection()
        elif choice == '2':
            max_turns = input("Максимум ходов (по умолчанию 10): ").strip()
            max_turns = int(max_turns) if max_turns.isdigit() else 10
            
            debug_client = DebugClient(debug_mode=True)
            debug_client.run_debug_session(max_turns)
        elif choice == '3':
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор")
