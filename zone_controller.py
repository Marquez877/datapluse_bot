#!/usr/bin/env python3
"""
⚡ СИСТЕМА ГЕОМЕТРИЧЕСКОГО РОСТА И КОНТРОЛЯ ЗОНЫ
Команда MACAN team: доминирование через численность!
"""

import math
from collections import defaultdict

class ZoneController:
    def __init__(self):
        self.controlled_zones = set()
        self.expansion_targets = []
        self.growth_rate = 1.2  # Геометрический коэффициент
        
    def calculate_hex_distance(self, pos1, pos2):
        """Расстояние между гексами"""
        q1, r1 = pos1
        q2, r2 = pos2
        return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) / 2
    
    def get_neighbors(self, q, r):
        """Соседние гексы"""
        return [
            (q + 1, r), (q - 1, r),
            (q, r + 1), (q, r - 1),
            (q + 1, r - 1), (q - 1, r + 1)
        ]
    
    def analyze_territory(self, arena_data):
        """Анализ территории и зон влияния"""
        ants = arena_data.get('ants', [])
        food_sources = arena_data.get('food', [])
        
        our_positions = [(ant['q'], ant['r']) for ant in ants]
        food_positions = [(food['q'], food['r']) for food in food_sources]
        
        # Зоны контроля (радиус 3 гекса от каждого муравья)
        control_map = defaultdict(int)
        for pos in our_positions:
            for dist in range(1, 4):  # радиус 3
                for neighbor in self.get_hex_ring(pos, dist):
                    control_map[neighbor] += 4 - dist  # убывающий вес
        
        # Приоритетные зоны для расширения
        expansion_zones = []
        for food_pos in food_positions:
            if food_pos not in our_positions:
                score = self.calculate_expansion_score(food_pos, our_positions, control_map)
                expansion_zones.append((food_pos, score))
        
        expansion_zones.sort(key=lambda x: x[1], reverse=True)
        return expansion_zones[:5]  # Топ-5 зон для расширения
    
    def get_hex_ring(self, center, radius):
        """Получить кольцо гексов на определенном расстоянии"""
        if radius == 0:
            return [center]
            
        results = []
        q, r = center
        
        # Алгоритм кольца для гексагональной сетки
        for i in range(6):  # 6 направлений
            for j in range(radius):
                # Вычисления для каждого направления
                current_q = q + self.hex_directions[i][0] * radius + self.hex_directions[(i + 1) % 6][0] * j
                current_r = r + self.hex_directions[i][1] * radius + self.hex_directions[(i + 1) % 6][1] * j
                results.append((current_q, current_r))
        
        return results
    
    @property
    def hex_directions(self):
        """6 направлений в гексагональной сетке"""
        return [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
    
    def calculate_expansion_score(self, target_pos, our_positions, control_map):
        """Расчет приоритета зоны для расширения"""
        q, r = target_pos
        
        # Базовая оценка: обратное расстояние до ближайшего муравья
        min_distance = min(self.calculate_hex_distance(target_pos, pos) for pos in our_positions)
        distance_score = 100 / max(1, min_distance)
        
        # Бонус за слабый контроль (легче захватить)
        control_score = max(0, 50 - control_map.get(target_pos, 0))
        
        # Бонус за соседство с нашими позициями
        adjacency_score = sum(
            20 for neighbor in self.get_neighbors(q, r) 
            if neighbor in our_positions
        )
        
        # Стратегическая ценность (центральность)
        centrality_score = 100 / max(1, abs(q) + abs(r) + abs(q + r))
        
        return distance_score + control_score + adjacency_score + centrality_score
    
    def plan_geometric_growth(self, current_ant_count, target_multiplier=2.0):
        """Планирование геометрического роста"""
        turns_needed = math.ceil(math.log(target_multiplier) / math.log(self.growth_rate))
        
        growth_plan = []
        for turn in range(1, turns_needed + 1):
            expected_count = int(current_ant_count * (self.growth_rate ** turn))
            growth_plan.append({
                'turn': turn,
                'target_ants': expected_count,
                'growth_rate': self.growth_rate
            })
        
        return growth_plan
    
    def calculate_optimal_composition(self, total_ants):
        """Оптимальный состав армии"""
        if total_ants < 4:
            return {'workers': total_ants, 'fighters': 0, 'scouts': 0}
        
        # Для быстрого роста: 70% рабочие, 25% бойцы, 5% разведчики
        workers = int(total_ants * 0.70)
        fighters = int(total_ants * 0.25)
        scouts = total_ants - workers - fighters
        
        return {
            'workers': max(1, workers),
            'fighters': max(0, fighters),
            'scouts': max(0, scouts)
        }
    
    def identify_chokepoints(self, arena_data):
        """Определение стратегических точек"""
        obstacles = set()
        if 'obstacles' in arena_data:
            obstacles = {(obs['q'], obs['r']) for obs in arena_data['obstacles']}
        
        # Анализ узких проходов и стратегических позиций
        chokepoints = []
        food_positions = [(food['q'], food['r']) for food in arena_data.get('food', [])]
        
        for food_pos in food_positions:
            neighbors = self.get_neighbors(*food_pos)
            blocked_neighbors = sum(1 for n in neighbors if n in obstacles)
            
            if blocked_neighbors >= 3:  # Узкий проход
                chokepoints.append({
                    'position': food_pos,
                    'strategic_value': 80 + blocked_neighbors * 10,
                    'type': 'chokepoint'
                })
        
        return sorted(chokepoints, key=lambda x: x['strategic_value'], reverse=True)
