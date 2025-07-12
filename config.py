import os
import requests
from dotenv import load_dotenv
import random
import json 
import math
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

load_dotenv()

TOKEN = os.getenv("TOKEN")
HEADERS = {"Content-Type": "application/json",
            "Accept": "application/json",
            "X-Auth-Token": TOKEN}

# Правильные URL для API (не документация!)
BASE_URL_TEST = "https://games-test.datsteam.dev/api"  # Тестовый сервер
BASE_URL_PROD = "https://games.datsteam.dev/api"      # Боевой сервер
BASE_URL = BASE_URL_TEST  # По умолчанию используем тестовый

data = {
    "name": "MACAN team",
    "members": [
        "Эрмек Озгонбеков",
        "Элдияр Адылбеков", 
        "Каныкей Ашыракманова"
    ]
}

# Константы типов муравьев
ROLE_WORKER = 0
ROLE_FIGHTER = 1
ROLE_SCOUT = 2

# Константы типов гексов
HEX_ANTHILL = 1
HEX_EMPTY = 2
HEX_DIRT = 3
HEX_ACID = 4
HEX_STONE = 5

# Константы ресурсов
RESOURCE_APPLE = 1
RESOURCE_BREAD = 2
RESOURCE_NECTAR = 3

class AdvancedStrategy:
    def __init__(self):
        self.explored_hexes = set()
        self.enemy_positions = {}
        self.resource_memory = {}
        self.turn_count = 0
        self.threat_assessment = defaultdict(int)
        
    def update_memory(self, arena_data):
        """Обновляем память о карте, врагах и ресурсах"""
        self.turn_count += 1
        
        # Запоминаем исследованные гексы
        for hex_info in arena_data.get('map', []):
            self.explored_hexes.add((hex_info['q'], hex_info['r']))
            
        # Обновляем информацию о врагах
        for enemy in arena_data.get('enemies', []):
            pos = (enemy['q'], enemy['r'])
            self.enemy_positions[pos] = {
                'type': enemy['type'],
                'health': enemy['health'],
                'turn': self.turn_count
            }
            
        # Запоминаем ресурсы
        for food in arena_data.get('food', []):
            pos = (food['q'], food['r'])
            self.resource_memory[pos] = {
                'type': food['type'],
                'amount': food['amount'],
                'turn': self.turn_count
            }
            
    def hex_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Вычисление расстояния между гексами"""
        q1, r1 = pos1
        q2, r2 = pos2
        return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2
        
    def assess_threat_level(self, pos, arena_data):
        """Оценка уровня угрозы для позиции"""
        threat = 0
        enemies = arena_data.get('enemies', [])
        
        for enemy in enemies:
            enemy_pos = (enemy['q'], enemy['r'])
            distance = self.hex_distance(pos, enemy_pos)
            
            if enemy['type'] == ROLE_FIGHTER and distance <= 2:
                threat += 70 / (distance + 1)
            elif enemy['type'] == ROLE_SCOUT and distance <= 4:
                threat += 20 / (distance + 1)
            elif enemy['type'] == ROLE_WORKER and distance <= 1:
                threat += 30 / (distance + 1)
                
        return threat
        
    def find_safe_exploration_targets(self, ant, arena_data):
        """Находим безопасные цели для исследования"""
        ant_pos = (ant['q'], ant['r'])
        candidates = []
        
        # Генерируем потенциальные цели в радиусе движения
        for radius in range(1, ant['type'] == ROLE_SCOUT and 8 or 6):
            for q in range(-radius, radius + 1):
                for r in range(-radius, radius + 1):
                    if abs(q + r) <= radius:
                        target = (ant_pos[0] + q, ant_pos[1] + r)
                        if target not in self.explored_hexes:
                            threat = self.assess_threat_level(target, arena_data)
                            distance = self.hex_distance(ant_pos, target)
                            score = radius * 10 - threat - distance
                            candidates.append((target, score))
                            
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:5] if candidates else []

class APIclient:
    def __init__(self, use_test_server=True):
        self.token = TOKEN
        self.headers = HEADERS
        
        # Выбираем сервер
        if use_test_server:
            self.base_url = BASE_URL_TEST
            print("🧪 Используется ТЕСТОВЫЙ сервер")
        else:
            self.base_url = BASE_URL_PROD
            print("⚔️ Используется БОЕВОЙ сервер")
            
        self.strategy = AdvancedStrategy()
        self.request_count = 0  # Для отслеживания лимита 3 RPS
        self.last_request_time = 0
        
    def _rate_limit_check(self):
        """Проверка лимита запросов (3 RPS)"""
        import time
        current_time = time.time()
        if current_time - self.last_request_time < 0.34:  # ~1/3 секунды между запросами
            time.sleep(0.34 - (current_time - self.last_request_time))
        self.last_request_time = time.time()
        
    def get_arena(self):
        """Получение текущего состояния арены"""
        self._rate_limit_check()
        try:
            response = requests.get(f"{self.base_url}/arena", headers=self.headers)
            response.raise_for_status()
            data = response.json()
            self.strategy.update_memory(data)
            return data
        except requests.RequestException as e:
            print(f"Ошибка при получении данных арены: {e}")
            return None

    def send_move(self, moves):
        """Отправка команд движения"""
        self._rate_limit_check()
        try:
            response = requests.post(f"{self.base_url}/move", headers=self.headers, json={"moves": moves})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при отправке команд: {e}")
            return None
            
    def register_for_round(self):
        """Регистрация на раунд"""
        self._rate_limit_check()
        try:
            response = requests.post(f"{self.base_url}/register", headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при регистрации: {e}")
            return None
    
    def get_logs(self):
        """Получение журнала действий"""
        self._rate_limit_check()
        try:
            response = requests.get(f"{self.base_url}/logs", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при получении логов: {e}")
            return None
    
    def get_rounds_info(self):
        """Получение информации о раундах"""
        self._rate_limit_check()
        try:
            response = requests.get(f"{self.base_url}/rounds", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при получении информации о раундах: {e}")
            return None

    def validate_move_path(self, ant: Dict, path: List[Dict], arena_data: Dict) -> List[Dict]:
        """Валидация пути движения согласно правилам игры"""
        if not path or len(path) < 2:
            return path
            
        ant_type = ant['type']
        max_movement_points = {ROLE_WORKER: 5, ROLE_FIGHTER: 4, ROLE_SCOUT: 7}.get(ant_type, 5)
        
        validated_path = [path[0]]  # Стартовая позиция
        movement_spent = 0
        
        # Создаем карту стоимости движения
        hex_costs = {}
        for hex_info in arena_data.get('map', []):
            pos = (hex_info['q'], hex_info['r'])
            cost = hex_info.get('cost', 1)
            if hex_info['type'] == HEX_STONE:
                cost = float('inf')  # Непроходимый
            hex_costs[pos] = cost
        
        # Проверяем каждый шаг пути
        for i in range(1, len(path)):
            current_pos = (path[i-1]['q'], path[i-1]['r'])
            next_pos = (path[i]['q'], path[i]['r'])
            
            # Проверяем, что гексы соседние
            if next_pos not in self.get_neighbors(*current_pos):
                print(f"Предупреждение: несоседние гексы в пути муравья {ant['id']}")
                break
                
            # Проверяем стоимость движения
            move_cost = hex_costs.get(next_pos, 1)
            if move_cost == float('inf'):
                print(f"Предупреждение: попытка пройти через непроходимый гекс")
                break
                
            if movement_spent + move_cost > max_movement_points:
                print(f"Предупреждение: превышение очков движения для муравья {ant['id']}")
                break
                
            validated_path.append(path[i])
            movement_spent += move_cost
            
        return validated_path
    
    def check_collision_avoidance(self, moves: List[Dict], arena_data: Dict) -> List[Dict]:
        """Проверка и предотвращение коллизий между нашими муравьями"""
        our_ants = {ant['id']: ant for ant in arena_data.get('ants', [])}
        final_positions = {}
        
        # Вычисляем финальные позиции каждого муравья
        for move in moves:
            ant_id = move['ant']
            ant = our_ants.get(ant_id)
            if not ant:
                continue
                
            if move['path']:
                final_pos = (move['path'][-1]['q'], move['path'][-1]['r'])
            else:
                final_pos = (ant['q'], ant['r'])
                
            final_positions[ant_id] = final_pos
        
        # Проверяем конфликты (муравьи одного типа не могут быть на одном гексе)
        type_positions = defaultdict(list)
        for ant_id, pos in final_positions.items():
            ant = our_ants.get(ant_id)
            if ant:
                type_positions[ant['type']].append((ant_id, pos))
        
        # Устраняем конфликты
        cleaned_moves = []
        for move in moves:
            ant_id = move['ant']
            ant = our_ants.get(ant_id)
            if not ant:
                continue
                
            # Проверяем, есть ли конфликт с другими муравьями того же типа
            final_pos = final_positions[ant_id]
            same_type_ants = type_positions[ant['type']]
            
            conflict = False
            for other_ant_id, other_pos in same_type_ants:
                if other_ant_id != ant_id and other_pos == final_pos:
                    conflict = True
                    break
            
            if not conflict:
                cleaned_moves.append(move)
            else:
                print(f"Предупреждение: конфликт позиций для муравья {ant_id}, команда отменена")
                
        return cleaned_moves

    @staticmethod
    def hex_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Вычисление расстояния между гексами"""
        q1, r1 = pos1
        q2, r2 = pos2
        return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2

    @staticmethod
    def get_neighbors(q: int, r: int) -> List[Tuple[int, int]]:
        """Получение соседних гексов"""
        directions = [(+1, 0), (+1, -1), (0, -1), (-1, 0), (-1, +1), (0, +1)]
        return [(q + dq, r + dr) for dq, dr in directions]

    def find_path_astar(self, start: Tuple[int, int], goal: Tuple[int, int], 
                       arena_data: Dict, max_cost: int = 20) -> List[Dict]:
        """A* алгоритм для поиска оптимального пути"""
        from heapq import heappush, heappop
        
        open_set = [(0, start, [])]
        closed_set = set()
        
        # Создаем карту стоимости гексов
        hex_costs = {}
        for hex_info in arena_data.get('map', []):
            pos = (hex_info['q'], hex_info['r'])
            if hex_info['type'] == HEX_STONE:
                continue  # Непроходимый
            elif hex_info['type'] == HEX_ACID:
                hex_costs[pos] = 3  # Избегаем кислоту
            elif hex_info['type'] == HEX_DIRT:
                hex_costs[pos] = 2
            else:
                hex_costs[pos] = 1
                
        while open_set:
            f_cost, current, path = heappop(open_set)
            
            if current == goal:
                return [{'q': q, 'r': r} for q, r in [start] + path]
                
            if current in closed_set:
                continue
                
            closed_set.add(current)
            
            for neighbor in self.get_neighbors(*current):
                if neighbor in closed_set:
                    continue
                    
                move_cost = hex_costs.get(neighbor, 1)
                if move_cost > max_cost:
                    continue
                    
                new_path = path + [neighbor]
                g_cost = len(new_path)
                h_cost = self.hex_distance(neighbor, goal)
                f_cost = g_cost + h_cost
                
                heappush(open_set, (f_cost, neighbor, new_path))
                
        return [{'q': start[0], 'r': start[1]}]  # Остаемся на месте

    def get_optimal_resource_target(self, ant: Dict, visible_food: List[Dict], 
                                   home_coords: List[Dict]) -> Optional[Tuple[int, int]]:
        """Выбор оптимального ресурса для сбора"""
        if not visible_food:
            return None
            
        ant_pos = (ant['q'], ant['r'])
        scored_resources = []
        
        for food in visible_food:
            food_pos = (food['q'], food['r'])
            distance = self.hex_distance(ant_pos, food_pos)
            
            # Оценка ценности ресурса
            value_multiplier = {
                RESOURCE_NECTAR: 6,
                RESOURCE_BREAD: 2,
                RESOURCE_APPLE: 1
            }.get(food['type'], 1)
            
            # Учитываем расстояние до дома
            home_distance = min(self.hex_distance(food_pos, (h['q'], h['r'])) 
                               for h in home_coords)
            
            score = (food['amount'] * value_multiplier) / (distance + 1) - home_distance * 0.1
            scored_resources.append((food_pos, score))
            
        scored_resources.sort(key=lambda x: x[1], reverse=True)
        return scored_resources[0][0] if scored_resources else None

    def plan_worker_move(self, ant: Dict, visible_food: List[Dict], 
                        home_coords: List[Dict], arena_data: Dict) -> List[Dict]:
        """Планирование движения рабочего с улучшенной логикой"""
        ant_pos = (ant['q'], ant['r'])
        spot = arena_data.get('spot', {})
        main_hex = (spot.get('q', 0), spot.get('r', 0))
        
        # ВАЖНО: Освобождаем основной гекс для создания новых муравьев
        if ant_pos == main_hex:
            # Ищем ближайший свободный гекс рядом с муравейником
            for home in home_coords:
                home_pos = (home['q'], home['r'])
                if home_pos != main_hex:
                    return self.find_path_astar(ant_pos, home_pos, arena_data)
            
            # Если все гексы муравейника заняты, отходим на 1 гекс
            neighbors = self.get_neighbors(*ant_pos)
            if neighbors:
                return self.find_path_astar(ant_pos, neighbors[0], arena_data)
        
        # Если несем ресурсы, идем домой
        if ant.get('food') and ant['food'].get('amount', 0) > 0:
            # Выбираем ближайший гекс муравейника
            closest_home = min(home_coords, 
                             key=lambda h: self.hex_distance(ant_pos, (h['q'], h['r'])))
            target = (closest_home['q'], closest_home['r'])
            return self.find_path_astar(ant_pos, target, arena_data)
            
        # Ищем оптимальный ресурс
        target_pos = self.get_optimal_resource_target(ant, visible_food, home_coords)
        if target_pos:
            return self.find_path_astar(ant_pos, target_pos, arena_data)
            
        # Исследуем территорию рядом с домом
        home_center = home_coords[0] if home_coords else {'q': 0, 'r': 0}
        exploration_targets = self.strategy.find_safe_exploration_targets(ant, arena_data)
        
        if exploration_targets:
            # Фильтруем цели рядом с домом
            nearby_targets = [target for target, score in exploration_targets 
                            if self.hex_distance(target, (home_center['q'], home_center['r'])) <= 8]
            if nearby_targets:
                return self.find_path_astar(ant_pos, nearby_targets[0], arena_data)
                
        return [{'q': ant['q'], 'r': ant['r']}]

    def calculate_combat_effectiveness(self, attacker: Dict, target_pos: Tuple[int, int], 
                                     arena_data: Dict, our_ants: List[Dict]) -> float:
        """Расчет эффективности атаки с учетом бонусов"""
        base_damage = {ROLE_WORKER: 30, ROLE_FIGHTER: 70, ROLE_SCOUT: 20}.get(attacker['type'], 30)
        attacker_pos = (attacker['q'], attacker['r'])
        
        # Базовый урон
        damage = base_damage
        
        # Бонус поддержки (50% если рядом союзник)
        support_bonus = 0
        for ally in our_ants:
            if ally['id'] == attacker['id']:
                continue
            ally_pos = (ally['q'], ally['r'])
            
            # Проверяем, что союзник рядом с атакующим И целью
            if (self.hex_distance(ally_pos, attacker_pos) <= 1 and 
                self.hex_distance(ally_pos, target_pos) <= 1 and
                ally_pos != attacker_pos):  # Не на одном гексе
                support_bonus = 0.5
                break
        
        # Бонус муравейника (25% если в радиусе 2 от дома)
        anthill_bonus = 0
        home_coords = arena_data.get('home', [])
        for home in home_coords:
            home_pos = (home['q'], home['r'])
            if self.hex_distance(attacker_pos, home_pos) <= 2:
                anthill_bonus = 0.25
                break
        
        # Применяем бонусы
        total_multiplier = 1.0 + support_bonus + anthill_bonus
        final_damage = damage * total_multiplier
        
        return final_damage
        
    def should_attack_position(self, attacker: Dict, target_pos: Tuple[int, int], 
                              arena_data: Dict, our_ants: List[Dict]) -> bool:
        """Определяет, стоит ли атаковать данную позицию"""
        # Проверяем, есть ли враг на этой позиции
        enemies = arena_data.get('enemies', [])
        target_enemy = None
        
        for enemy in enemies:
            if (enemy['q'], enemy['r']) == target_pos:
                target_enemy = enemy
                break
                
        if not target_enemy:
            return False
            
        # Рассчитываем наш урон
        our_damage = self.calculate_combat_effectiveness(attacker, target_pos, arena_data, our_ants)
        
        # Рассчитываем урон врага (если он сможет атаковать в ответ)
        enemy_damage = {ROLE_WORKER: 30, ROLE_FIGHTER: 70, ROLE_SCOUT: 20}.get(target_enemy['type'], 30)
        
        # Учитываем здоровье
        our_health = attacker['health']
        enemy_health = target_enemy['health']
        
        # Простая эвристика: атакуем если можем убить за 1-2 хода или у нас большое преимущество
        turns_to_kill_enemy = max(1, enemy_health // our_damage)
        turns_to_kill_us = max(1, our_health // enemy_damage) if enemy_damage > 0 else float('inf')
        
        return turns_to_kill_enemy <= turns_to_kill_us or our_damage > enemy_health

    def plan_fighter_move(self, ant: Dict, visible_enemies: List[Dict], 
                         arena_data: Dict, our_ants: List[Dict]) -> List[Dict]:
        """Планирование движения бойца с тактикой"""
        ant_pos = (ant['q'], ant['r'])
        spot = arena_data.get('spot', {})
        main_hex = (spot.get('q', 0), spot.get('r', 0))
        home_coords = arena_data.get('home', [])
        
        # ВАЖНО: Освобождаем основной гекс для создания новых муравьев
        if ant_pos == main_hex:
            # Отходим на ближайший гекс для патрулирования
            neighbors = self.get_neighbors(*ant_pos)
            if neighbors:
                return self.find_path_astar(ant_pos, neighbors[0], arena_data)
        
        if not visible_enemies:
            # Патрулируем территорию
            patrol_targets = self.strategy.find_safe_exploration_targets(ant, arena_data)
            if patrol_targets:
                return self.find_path_astar(ant_pos, patrol_targets[0][0], arena_data)
            return [{'q': ant['q'], 'r': ant['r']}]
            
        # Приоритезируем цели
        priority_targets = []
        for enemy in visible_enemies:
            enemy_pos = (enemy['q'], enemy['r'])
            distance = self.hex_distance(ant_pos, enemy_pos)
            
            # Приоритет: рабочие > разведчики > бойцы
            priority = {ROLE_WORKER: 3, ROLE_SCOUT: 2, ROLE_FIGHTER: 1}.get(enemy['type'], 1)
            
            # Учитываем здоровье врага
            health_factor = 200 / (enemy['health'] + 1)
            
            # Проверяем поддержку союзников
            support = sum(1 for ally in our_ants 
                         if ally['type'] == ROLE_FIGHTER and 
                         self.hex_distance((ally['q'], ally['r']), enemy_pos) <= 2)
            
            score = priority * health_factor + support * 0.5 - distance * 0.1
            priority_targets.append((enemy_pos, score))
            
        priority_targets.sort(key=lambda x: x[1], reverse=True)
        target_pos = priority_targets[0][0]
        
        # Пытаемся окружить цель
        neighbors = self.get_neighbors(*target_pos)
        best_attack_pos = min(neighbors, 
                             key=lambda pos: self.hex_distance(ant_pos, pos))
        
        return self.find_path_astar(ant_pos, best_attack_pos, arena_data)

    def plan_scout_move(self, ant: Dict, arena_data: Dict) -> List[Dict]:
        """Планирование движения разведчика"""
        ant_pos = (ant['q'], ant['r'])
        spot = arena_data.get('spot', {})
        main_hex = (spot.get('q', 0), spot.get('r', 0))
        
        # ВАЖНО: Освобождаем основной гекс для создания новых муравьев
        if ant_pos == main_hex:
            # Отходим для разведки
            exploration_targets = self.strategy.find_safe_exploration_targets(ant, arena_data)
            if exploration_targets:
                return self.find_path_astar(ant_pos, exploration_targets[0][0], arena_data)
            
            # Если нет целей для разведки, отходим на соседний гекс
            neighbors = self.get_neighbors(*ant_pos)
            if neighbors:
                return self.find_path_astar(ant_pos, neighbors[0], arena_data)
        
        # Ищем неисследованные области
        exploration_targets = self.strategy.find_safe_exploration_targets(ant, arena_data)
        
        if exploration_targets:
            # Выбираем самую перспективную цель
            target_pos = exploration_targets[0][0]
            return self.find_path_astar(ant_pos, target_pos, arena_data)
            
        # Если все исследовано, патрулируем периметр
        home_coords = arena_data.get('home', [])
        if home_coords:
            home_center = home_coords[0]
            # Движемся по кругу вокруг базы
            angle = (self.strategy.turn_count * 0.5) % (2 * math.pi)
            radius = 10
            target_q = int(home_center['q'] + radius * math.cos(angle))
            target_r = int(home_center['r'] + radius * math.sin(angle))
            return self.find_path_astar(ant_pos, (target_q, target_r), arena_data)
            
        return [{'q': ant['q'], 'r': ant['r']}]

    def execute_turn(self):
        """Основной цикл выполнения хода с полной валидацией"""
        arena_data = self.get_arena()
        if not arena_data:
            return False
            
        moves = []
        our_ants = arena_data.get('ants', [])
        visible_enemies = arena_data.get('enemies', [])
        visible_food = arena_data.get('food', [])
        home_coords = arena_data.get('home', [])
        
        print(f"\n=== ХОД {self.strategy.turn_count} ===")
        print(f"Наших муравьев: {len(our_ants)}")
        print(f"Видимых врагов: {len(visible_enemies)}")
        print(f"Видимых ресурсов: {len(visible_food)}")
        print(f"Текущий счет: {arena_data.get('score', 0)}")
        
        for ant in our_ants:
            ant_type = ant['type']
            ant_type_name = {ROLE_WORKER: 'Рабочий', ROLE_FIGHTER: 'Боец', ROLE_SCOUT: 'Разведчик'}.get(ant_type, 'Неизвестный')
            
            try:
                if ant_type == ROLE_WORKER:
                    path = self.plan_worker_move(ant, visible_food, home_coords, arena_data)
                elif ant_type == ROLE_FIGHTER:
                    path = self.plan_fighter_move(ant, visible_enemies, arena_data, our_ants)
                elif ant_type == ROLE_SCOUT:
                    path = self.plan_scout_move(ant, arena_data)
                else:
                    path = [{'q': ant['q'], 'r': ant['r']}]
                
                # Валидируем путь
                validated_path = self.validate_move_path(ant, path, arena_data)
                
                if len(validated_path) > 1:  # Есть движение
                    moves.append({
                        "ant": ant['id'],
                        "path": validated_path[1:]  # Исключаем текущую позицию
                    })
                    print(f"{ant_type_name} {ant['id'][:8]}: движение на {len(validated_path)-1} шагов")
                else:
                    print(f"{ant_type_name} {ant['id'][:8]}: остается на месте")
                    
            except Exception as e:
                print(f"Ошибка планирования для {ant_type_name} {ant['id'][:8]}: {e}")
                
        # Проверяем коллизии между нашими муравьями
        moves = self.check_collision_avoidance(moves, arena_data)
        
        # Отправляем команды
        if moves:
            result = self.send_move(moves)
            if result is None:
                print("❌ Ошибка отправки команд")
                return False
            else:
                print(f"✅ Отправлено {len(moves)} команд")
        else:
            print("ℹ️ Нет команд для отправки")
            
        print(f"До следующего хода: {arena_data.get('nextTurnIn', 0):.1f} сек")
        print("=" * 40)
        
        return True

def main():
    """Основная функция для запуска бота"""
    import sys
    
    # Проверяем аргументы командной строки
    use_test_server = True
    if len(sys.argv) > 1 and sys.argv[1] == "--prod":
        use_test_server = False
        print("⚠️  ВНИМАНИЕ: Запуск на БОЕВОМ сервере!")
        confirm = input("Введите 'YES' для подтверждения: ")
        if confirm != 'YES':
            print("Запуск отменен")
            return
    
    client = APIclient(use_test_server=use_test_server)
    
    # Регистрируемся на раунд
    print("📝 Регистрируемся на раунд...")
    registration_result = client.register_for_round()
    if registration_result:
        print("✅ Успешно зарегистрированы на раунд!")
        print(f"Команда: {data['name']}")
    else:
        print("❌ Не удалось зарегистрироваться")
        return
        
    # Основной игровой цикл
    try:
        print("🎮 Начинаем игру...")
        while True:
            arena_data = client.get_arena()
            if arena_data and arena_data.get('nextTurnIn', 0) > 0:
                client.execute_turn()
                import time
                time.sleep(2)  # Ждем между ходами
            else:
                print("🏁 Раунд завершен или нет данных")
                break
    except KeyboardInterrupt:
        print("\n⏹️  Остановлено пользователем")
    except Exception as e:
        print(f"💥 Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()