#!/usr/bin/env python3
"""
🚀 УЛЬТРА-АГРЕССИВНАЯ СИСТЕМА DOMINATION 
Команда MACAN team: Эрмек Озгонбеков, Элдияр Адылбеков, Каныкей Ашыракманова

ЦЕЛИ:
1. ГЕОМЕТРИЧЕСКИЙ РОСТ муравьев до 100
2. МАКСИМАЛЬНЫЙ сбор ресурсов  
3. ДОМИНИРОВАНИЕ через координацию
4. УНИЧТОЖЕНИЕ врагов армией
"""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import time
import random
from typing import Dict, List, Tuple, Optional
from config import *

class UltraAgressiveStrategy:
    def __init__(self):
        self.explored_hexes = set()
        self.enemy_positions = {}
        self.resource_memory = {}
        self.turn_count = 0
        self.threat_assessment = defaultdict(int)
        
        # НОВЫЕ СИСТЕМЫ ДОМИНИРОВАНИЯ
        self.ant_assignments = {}  # ID -> специальная задача
        self.resource_claims = {}  # позиция -> ID муравья
        self.formation_groups = defaultdict(list)  # тип формации -> муравьи
        self.expansion_zones = []  # приоритетные зоны расширения
        self.blocked_positions = set()  # заблокированные позиции
        self.last_successful_moves = {}  # ID -> последний успешный путь
        
        # СЧЕТЧИКИ ЭФФЕКТИВНОСТИ
        self.moves_blocked = 0
        self.resources_collected = 0
        self.territory_controlled = 0
        
    def assign_specialized_roles(self, ants: List[Dict], arena_data: Dict):
        """СПЕЦИАЛИЗАЦИЯ: каждому муравью - четкая роль"""
        home_coords = arena_data.get('home', [])
        visible_food = arena_data.get('food', [])
        spot = arena_data.get('spot', {})
        main_hex = (spot.get('q', 0), spot.get('r', 0))
        
        # Очищаем старые назначения
        self.ant_assignments.clear()
        self.formation_groups.clear()
        
        workers = [ant for ant in ants if ant['type'] == ROLE_WORKER]
        fighters = [ant for ant in ants if ant['type'] == ROLE_FIGHTER] 
        scouts = [ant for ant in ants if ant['type'] == ROLE_SCOUT]
        
        # РАБОЧИЕ: специализация по ресурсам
        for i, worker in enumerate(workers):
            worker_pos = (worker['q'], worker['r'])
            
            if worker_pos == main_hex:
                self.ant_assignments[worker['id']] = "EVACUATE_MAIN_HEX"
            elif worker.get('food') and worker['food'].get('amount', 0) > 0:
                self.ant_assignments[worker['id']] = "DELIVER_RESOURCES"
            elif i < len(visible_food):
                # Назначаем каждому рабочему свой ресурс
                target_food = visible_food[i % len(visible_food)]
                self.ant_assignments[worker['id']] = f"COLLECT_{target_food['q']}_{target_food['r']}"
                self.resource_claims[(target_food['q'], target_food['r'])] = worker['id']
            else:
                self.ant_assignments[worker['id']] = "EXPLORE_RESOURCES"
        
        # БОЙЦЫ: формирование боевых групп
        for i, fighter in enumerate(fighters):
            fighter_pos = (fighter['q'], fighter['r'])
            
            if fighter_pos == main_hex:
                self.ant_assignments[fighter['id']] = "EVACUATE_MAIN_HEX"
            elif len(fighters) >= 3:  # Есть армия для атак
                group_id = i // 3  # Группы по 3
                self.formation_groups[f"ATTACK_SQUAD_{group_id}"].append(fighter['id'])
                self.ant_assignments[fighter['id']] = f"ATTACK_FORMATION_{group_id}"
            else:
                self.ant_assignments[fighter['id']] = "DEFEND_BASE"
        
        # РАЗВЕДЧИКИ: зоны исследования  
        for i, scout in enumerate(scouts):
            scout_pos = (scout['q'], scout['r'])
            
            if scout_pos == main_hex:
                self.ant_assignments[scout['id']] = "EVACUATE_MAIN_HEX"
            else:
                zone_id = i % 4  # 4 зоны исследования
                self.ant_assignments[scout['id']] = f"SCOUT_ZONE_{zone_id}"
                
    def resolve_position_conflicts(self, moves: List[Dict], ants: List[Dict]) -> List[Dict]:
        """ИНТЕЛЛЕКТУАЛЬНОЕ разрешение конфликтов позиций"""
        resolved_moves = []
        position_claims = defaultdict(list)
        
        # Группируем по целевым позициям
        for move in moves:
            if move.get('path'):
                final_pos = (move['path'][-1]['q'], move['path'][-1]['r'])
                position_claims[final_pos].append(move)
        
        for position, competing_moves in position_claims.items():
            if len(competing_moves) == 1:
                resolved_moves.extend(competing_moves)
            else:
                # РАЗРЕШЕНИЕ КОНФЛИКТА: приоритеты
                priority_move = self.select_priority_move(competing_moves, ants)
                resolved_moves.append(priority_move)
                
                # Остальным даем альтернативные пути
                for move in competing_moves:
                    if move != priority_move:
                        alternative = self.find_alternative_path(move, ants, position)
                        if alternative:
                            resolved_moves.append(alternative)
        
        return resolved_moves
    
    def select_priority_move(self, competing_moves: List[Dict], ants: List[Dict]) -> Dict:
        """Выбор приоритетного движения при конфликте"""
        ant_priorities = {}
        
        for move in competing_moves:
            ant_id = move['ant']
            ant = next((a for a in ants if a['id'] == ant_id), None)
            if not ant:
                continue
                
            priority = 0
            assignment = self.ant_assignments.get(ant_id, "")
            
            # ПРИОРИТЕТЫ (чем больше число - тем выше приоритет)
            if "DELIVER_RESOURCES" in assignment:
                priority = 100  # Доставка ресурсов - высший приоритет
            elif "COLLECT_" in assignment:
                priority = 90   # Сбор ресурсов
            elif "EVACUATE_MAIN_HEX" in assignment:
                priority = 80   # Освобождение главного гекса
            elif "ATTACK_FORMATION" in assignment:
                priority = 70   # Боевые формации
            elif ant['type'] == ROLE_WORKER:
                priority = 60   # Рабочие важнее
            elif ant['type'] == ROLE_FIGHTER:
                priority = 50   # Бойцы
            else:
                priority = 40   # Разведчики
                
            ant_priorities[move] = priority
        
        return max(competing_moves, key=lambda m: ant_priorities.get(m, 0))
    
    def find_alternative_path(self, blocked_move: Dict, ants: List[Dict], blocked_position: Tuple) -> Optional[Dict]:
        """Поиск альтернативного пути при блокировке"""
        ant_id = blocked_move['ant']
        ant = next((a for a in ants if a['id'] == ant_id), None)
        if not ant:
            return None
            
        ant_pos = (ant['q'], ant['r'])
        
        # Ищем соседние позиции как альтернативу
        neighbors = self.get_neighbors(*blocked_position)
        for neighbor in neighbors:
            if neighbor != ant_pos and neighbor not in self.blocked_positions:
                # Создаем альтернативный путь
                alternative_path = [{'q': neighbor[0], 'r': neighbor[1]}]
                return {
                    "ant": ant_id,
                    "path": alternative_path
                }
        
        return None
    
    def get_neighbors(self, q: int, r: int) -> List[Tuple[int, int]]:
        """Получение соседних гексов"""
        directions = [(+1, 0), (+1, -1), (0, -1), (-1, 0), (-1, +1), (0, +1)]
        return [(q + dq, r + dr) for dq, dr in directions]
        
    def create_expansion_zones(self, home_coords: List[Dict], arena_data: Dict):
        """Создание зон для агрессивной экспансии"""
        self.expansion_zones.clear()
        
        if not home_coords:
            return
            
        home_center = home_coords[0]
        center_pos = (home_center['q'], home_center['r'])
        
        # Создаем зоны в разных направлениях от базы
        directions = [
            (10, 0),    # Восток
            (5, 8),     # Северо-восток  
            (-5, 8),    # Северо-запад
            (-10, 0),   # Запад
            (-5, -8),   # Юго-запад
            (5, -8)     # Юго-восток
        ]
        
        for i, (dq, dr) in enumerate(directions):
            zone_center = (center_pos[0] + dq, center_pos[1] + dr)
            self.expansion_zones.append({
                'id': i,
                'center': zone_center,
                'priority': 10 - i,  # Первые зоны важнее
                'explored': False
            })

class SuperAgressiveAPIClient(APIclient):
    def __init__(self, use_test_server=True):
        super().__init__(use_test_server)
        self.strategy = UltraAgressiveStrategy()
        self.move_executor = ThreadPoolExecutor(max_workers=4)
        
    def execute_ultra_aggressive_turn(self):
        """УЛЬТРА-АГРЕССИВНОЕ выполнение хода с многопоточностью"""
        start_time = time.time()
        
        arena_data = self.get_arena()
        if not arena_data:
            return False
            
        our_ants = arena_data.get('ants', [])
        visible_enemies = arena_data.get('enemies', [])
        visible_food = arena_data.get('food', [])
        home_coords = arena_data.get('home', [])
        
        print(f"\n🚀 УЛЬТРА-АГРЕССИВНЫЙ ХОД {self.strategy.turn_count}")
        print(f"Армия: {len(our_ants)} | Враги: {len(visible_enemies)} | Ресурсы: {len(visible_food)} | Счет: {arena_data.get('score', 0)}")
        
        # 1. БЫСТРАЯ СПЕЦИАЛИЗАЦИЯ РОЛЕЙ
        self.strategy.assign_specialized_roles(our_ants, arena_data)
        
        # 2. СОЗДАНИЕ ЗОН ЭКСПАНСИИ
        self.strategy.create_expansion_zones(home_coords, arena_data)
        
        # 3. ПАРАЛЛЕЛЬНОЕ ПЛАНИРОВАНИЕ ДВИЖЕНИЙ
        futures = []
        for ant in our_ants:
            future = self.move_executor.submit(self.plan_specialized_move, ant, arena_data)
            futures.append((ant['id'], future))
        
        # 4. СБОР РЕЗУЛЬТАТОВ
        moves = []
        for ant_id, future in futures:
            try:
                path = future.result(timeout=0.5)  # Быстро получаем результат
                if path and len(path) > 1:
                    moves.append({
                        "ant": ant_id,
                        "path": path[1:]  # Исключаем текущую позицию
                    })
            except Exception as e:
                print(f"⚠️ Ошибка планирования для {ant_id[:8]}: {e}")
        
        # 5. ИНТЕЛЛЕКТУАЛЬНОЕ РАЗРЕШЕНИЕ КОНФЛИКТОВ
        resolved_moves = self.strategy.resolve_position_conflicts(moves, our_ants)
        
        # 6. ОТПРАВКА КОМАНД
        if resolved_moves:
            result = self.send_move(resolved_moves)
            if result:
                print(f"✅ ДОМИНАЦИЯ: {len(resolved_moves)} команд | Конфликтов решено: {len(moves) - len(resolved_moves)}")
                self.strategy.moves_blocked = len(moves) - len(resolved_moves)
            else:
                print("❌ Ошибка отправки команд")
                return False
        else:
            print("⚠️ Нет команд для отправки")
        
        execution_time = time.time() - start_time
        print(f"⚡ Время выполнения: {execution_time:.2f}с | Эффективность: {len(resolved_moves)/max(1, len(our_ants))*100:.1f}%")
        print("=" * 60)
        
        return True
    
    def plan_specialized_move(self, ant: Dict, arena_data: Dict) -> List[Dict]:
        """Планирование движения на основе специализации"""
        ant_id = ant['id']
        ant_pos = (ant['q'], ant['r'])
        assignment = self.strategy.ant_assignments.get(ant_id, "")
        
        try:
            if "EVACUATE_MAIN_HEX" in assignment:
                return self.evacuate_from_main_hex(ant, arena_data)
            elif "DELIVER_RESOURCES" in assignment:
                return self.deliver_resources_optimized(ant, arena_data)
            elif "COLLECT_" in assignment:
                return self.collect_assigned_resource(ant, assignment, arena_data)
            elif "EXPLORE_RESOURCES" in assignment:
                return self.explore_for_resources_aggressive(ant, arena_data)
            elif "ATTACK_FORMATION" in assignment:
                return self.execute_attack_formation(ant, assignment, arena_data)
            elif "DEFEND_BASE" in assignment:
                return self.defend_base_position(ant, arena_data)
            elif "SCOUT_ZONE" in assignment:
                return self.scout_assigned_zone(ant, assignment, arena_data)
            else:
                return self.default_aggressive_move(ant, arena_data)
                
        except Exception as e:
            print(f"Ошибка в специализированном планировании для {ant_id[:8]}: {e}")
            return [{'q': ant['q'], 'r': ant['r']}]
    
    def evacuate_from_main_hex(self, ant: Dict, arena_data: Dict) -> List[Dict]:
        """БЫСТРАЯ эвакуация с основного гекса"""
        ant_pos = (ant['q'], ant['r'])
        home_coords = arena_data.get('home', [])
        
        # Ищем ближайший свободный гекс дома
        for home in home_coords:
            home_pos = (home['q'], home['r'])
            if home_pos != ant_pos:
                return self.find_path_astar(ant_pos, home_pos, arena_data, max_cost=5)
        
        # Если все гексы дома заняты, отходим на соседний
        neighbors = self.get_neighbors(*ant_pos)
        if neighbors:
            return [{'q': ant_pos[0], 'r': ant_pos[1]}, {'q': neighbors[0][0], 'r': neighbors[0][1]}]
        
        return [{'q': ant['q'], 'r': ant['r']}]
    
    def collect_assigned_resource(self, ant: Dict, assignment: str, arena_data: Dict) -> List[Dict]:
        """Сбор НАЗНАЧЕННОГО ресурса"""
        # Извлекаем координаты из назначения: "COLLECT_125_-102"
        parts = assignment.split('_')
        if len(parts) >= 3:
            try:
                target_q = int(parts[1])
                target_r = int(parts[2])
                target_pos = (target_q, target_r)
                ant_pos = (ant['q'], ant['r'])
                
                return self.find_path_astar(ant_pos, target_pos, arena_data, max_cost=10)
            except ValueError:
                pass
        
        # Если не удалось извлечь координаты, ищем ближайший ресурс
        return self.explore_for_resources_aggressive(ant, arena_data)
    
    def explore_for_resources_aggressive(self, ant: Dict, arena_data: Dict) -> List[Dict]:
        """АГРЕССИВНАЯ разведка ресурсов"""
        ant_pos = (ant['q'], ant['r'])
        visible_food = arena_data.get('food', [])
        
        if visible_food:
            # Ищем ближайший НЕзанятый ресурс
            available_food = []
            for food in visible_food:
                food_pos = (food['q'], food['r'])
                if food_pos not in self.strategy.resource_claims:
                    distance = self.hex_distance(ant_pos, food_pos)
                    available_food.append((food_pos, distance))
            
            if available_food:
                available_food.sort(key=lambda x: x[1])
                target_pos = available_food[0][0]
                return self.find_path_astar(ant_pos, target_pos, arena_data, max_cost=15)
        
        # Если нет видимых ресурсов, АГРЕССИВНО исследуем
        home_coords = arena_data.get('home', [])
        if home_coords:
            home_center = home_coords[0]
            
            # Исследуем в случайном направлении ОТ базы
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.randint(8, 15)  # Дальние разведки
            
            target_q = int(home_center['q'] + distance * math.cos(angle))
            target_r = int(home_center['r'] + distance * math.sin(angle))
            target_pos = (target_q, target_r)
            
            return self.find_path_astar(ant_pos, target_pos, arena_data, max_cost=20)
        
        return [{'q': ant['q'], 'r': ant['r']}]
        
    def deliver_resources_optimized(self, ant: Dict, arena_data: Dict) -> List[Dict]:
        """ОПТИМИЗИРОВАННАЯ доставка ресурсов"""
        ant_pos = (ant['q'], ant['r'])
        home_coords = arena_data.get('home', [])
        
        if home_coords:
            # Выбираем ближайший гекс муравейника
            closest_home = min(home_coords, 
                             key=lambda h: self.hex_distance(ant_pos, (h['q'], h['r'])))
            target_pos = (closest_home['q'], closest_home['r'])
            
            return self.find_path_astar(ant_pos, target_pos, arena_data, max_cost=10)
        
        return [{'q': ant['q'], 'r': ant['r']}]

def main_ultra_aggressive():
    """ГЛАВНАЯ функция ультра-агрессивного бота"""
    print("🚀 ЗАПУСК УЛЬТРА-АГРЕССИВНОЙ СИСТЕМЫ DOMINATION")
    print("Команда MACAN team готова к ДОМИНИРОВАНИЮ!")
    print("=" * 60)
    
    client = SuperAgressiveAPIClient(use_test_server=True)
    
    try:
        turn_count = 0
        max_turns = 1000  # Лимит ходов
        
        while turn_count < max_turns:
            arena_data = client.get_arena()
            
            if not arena_data:
                print("❌ Нет данных арены, пауза...")
                time.sleep(2)
                continue
                
            next_turn_in = arena_data.get('nextTurnIn', 0)
            if next_turn_in <= 0:
                print("🏁 РАУНД ЗАВЕРШЕН!")
                break
            
            # ВЫПОЛНЯЕМ УЛЬТРА-АГРЕССИВНЫЙ ХОД
            success = client.execute_ultra_aggressive_turn()
            
            if success:
                turn_count += 1
                
                # Статистика каждые 10 ходов
                if turn_count % 10 == 0:
                    ants_count = len(arena_data.get('ants', []))
                    score = arena_data.get('score', 0)
                    print(f"📊 ПРОГРЕСС: Ход {turn_count} | Армия: {ants_count} | Счет: {score}")
            
            # Адаптивная пауза
            sleep_time = max(0.3, next_turn_in - 0.2)
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print(f"\n⏹️ ОСТАНОВКА на ходу {turn_count}")
    except Exception as e:
        print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.move_executor.shutdown(wait=True)
        print("🔥 УЛЬТРА-АГРЕССИВНАЯ СИСТЕМА ЗАВЕРШЕНА")

if __name__ == "__main__":
    main_ultra_aggressive()
