"""
Продвинутые стратегические алгоритмы для DatsPulse
"""
import math
from typing import List, Dict, Tuple, Set
from collections import defaultdict, deque

class TacticalFormations:
    """Класс для управления тактическими формациями"""
    
    @staticmethod
    def create_defensive_formation(fighters: List[Dict], home_coords: List[Dict]) -> Dict[str, Tuple[int, int]]:
        """Создает оборонительную формацию вокруг муравейника"""
        if not fighters or not home_coords:
            return {}
            
        home_center = home_coords[0]
        center = (home_center['q'], home_center['r'])
        
        # Позиции для обороны (кольцо вокруг базы)
        defensive_positions = []
        for radius in [3, 4]:
            for angle in range(0, 360, 60):  # 6 позиций на кольцо
                rad = math.radians(angle)
                q = int(center[0] + radius * math.cos(rad))
                r = int(center[1] + radius * math.sin(rad))
                defensive_positions.append((q, r))
        
        # Назначаем позиции бойцам
        assignments = {}
        for i, fighter in enumerate(fighters):
            if i < len(defensive_positions):
                assignments[fighter['id']] = defensive_positions[i]
                
        return assignments

    @staticmethod
    def create_attack_formation(fighters: List[Dict], target: Tuple[int, int]) -> Dict[str, Tuple[int, int]]:
        """Создает атакующую формацию для окружения цели"""
        if not fighters:
            return {}
            
        # Позиции для окружения цели
        neighbors = []
        directions = [(+1, 0), (+1, -1), (0, -1), (-1, 0), (-1, +1), (0, +1)]
        for dq, dr in directions:
            neighbors.append((target[0] + dq, target[1] + dr))
            
        assignments = {}
        for i, fighter in enumerate(fighters):
            if i < len(neighbors):
                assignments[fighter['id']] = neighbors[i]
                
        return assignments

class ResourceManager:
    """Менеджер ресурсов для оптимизации сбора"""
    
    def __init__(self):
        self.resource_claims = {}  # Кто какой ресурс собирает
        
    def assign_resources(self, workers: List[Dict], resources: List[Dict], 
                        home_coords: List[Dict]) -> Dict[str, Tuple[int, int]]:
        """Умное распределение ресурсов между рабочими"""
        if not workers or not resources:
            return {}
            
        # Очищаем устаревшие заявки
        active_worker_ids = {w['id'] for w in workers}
        self.resource_claims = {wid: pos for wid, pos in self.resource_claims.items() 
                               if wid in active_worker_ids}
        
        assignments = {}
        available_resources = []
        
        # Фильтруем уже заявленные ресурсы
        claimed_positions = set(self.resource_claims.values())
        for resource in resources:
            pos = (resource['q'], resource['r'])
            if pos not in claimed_positions:
                available_resources.append(resource)
                
        # Сортируем рабочих по приоритету (те, кто ближе к дому, имеют приоритет)
        if home_coords:
            home_center = (home_coords[0]['q'], home_coords[0]['r'])
            workers.sort(key=lambda w: self.hex_distance((w['q'], w['r']), home_center))
            
        # Назначаем ресурсы
        for worker in workers:
            if worker['id'] in self.resource_claims:
                assignments[worker['id']] = self.resource_claims[worker['id']]
                continue
                
            if not available_resources:
                break
                
            worker_pos = (worker['q'], worker['r'])
            
            # Находим лучший ресурс для этого рабочего
            best_resource = None
            best_score = -1
            
            for resource in available_resources:
                resource_pos = (resource['q'], resource['r'])
                distance = self.hex_distance(worker_pos, resource_pos)
                
                # Ценность ресурса
                value = {1: 10, 2: 20, 3: 60}.get(resource['type'], 10)
                score = (value * resource['amount']) / (distance + 1)
                
                if score > best_score:
                    best_score = score
                    best_resource = resource
                    
            if best_resource:
                pos = (best_resource['q'], best_resource['r'])
                assignments[worker['id']] = pos
                self.resource_claims[worker['id']] = pos
                available_resources.remove(best_resource)
                
        return assignments
    
    @staticmethod
    def hex_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        q1, r1 = pos1
        q2, r2 = pos2
        return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2

class ThreatAnalyzer:
    """Анализатор угроз для стратегического планирования"""
    
    def __init__(self):
        self.threat_history = defaultdict(list)
        
    def analyze_battlefield(self, arena_data: Dict) -> Dict:
        """Полный анализ поля боя"""
        enemies = arena_data.get('enemies', [])
        our_ants = arena_data.get('ants', [])
        
        analysis = {
            'enemy_strength': self.calculate_enemy_strength(enemies),
            'our_strength': self.calculate_our_strength(our_ants),
            'threat_zones': self.identify_threat_zones(enemies),
            'safe_zones': self.identify_safe_zones(arena_data),
            'recommended_strategy': None
        }
        
        # Рекомендуем стратегию
        if analysis['enemy_strength'] > analysis['our_strength'] * 1.5:
            analysis['recommended_strategy'] = 'defensive'
        elif analysis['our_strength'] > analysis['enemy_strength'] * 1.2:
            analysis['recommended_strategy'] = 'aggressive'
        else:
            analysis['recommended_strategy'] = 'balanced'
            
        return analysis
    
    def calculate_enemy_strength(self, enemies: List[Dict]) -> float:
        """Вычисляет общую силу врагов"""
        strength = 0
        for enemy in enemies:
            base_power = {0: 30, 1: 70, 2: 20}.get(enemy['type'], 30)
            health_ratio = enemy['health'] / {0: 130, 1: 180, 2: 80}.get(enemy['type'], 100)
            strength += base_power * health_ratio
        return strength
    
    def calculate_our_strength(self, our_ants: List[Dict]) -> float:
        """Вычисляет нашу общую силу"""
        strength = 0
        for ant in our_ants:
            base_power = {0: 30, 1: 70, 2: 20}.get(ant['type'], 30)
            health_ratio = ant['health'] / {0: 130, 1: 180, 2: 80}.get(ant['type'], 100)
            strength += base_power * health_ratio
        return strength
    
    def identify_threat_zones(self, enemies: List[Dict]) -> Set[Tuple[int, int]]:
        """Определяет опасные зоны на карте"""
        threat_zones = set()
        
        for enemy in enemies:
            enemy_pos = (enemy['q'], enemy['r'])
            threat_radius = {0: 2, 1: 3, 2: 4}.get(enemy['type'], 2)
            
            # Добавляем область вокруг врага в зону угрозы
            for q_offset in range(-threat_radius, threat_radius + 1):
                for r_offset in range(-threat_radius, threat_radius + 1):
                    if abs(q_offset + r_offset) <= threat_radius:
                        threat_pos = (enemy_pos[0] + q_offset, enemy_pos[1] + r_offset)
                        threat_zones.add(threat_pos)
                        
        return threat_zones
    
    def identify_safe_zones(self, arena_data: Dict) -> Set[Tuple[int, int]]:
        """Определяет безопасные зоны"""
        home_coords = arena_data.get('home', [])
        safe_zones = set()
        
        for home in home_coords:
            home_pos = (home['q'], home['r'])
            # Зона вокруг муравейника считается безопасной
            for q_offset in range(-3, 4):
                for r_offset in range(-3, 4):
                    if abs(q_offset + r_offset) <= 3:
                        safe_pos = (home_pos[0] + q_offset, home_pos[1] + r_offset)
                        safe_zones.add(safe_pos)
                        
        return safe_zones

class MapExplorer:
    """Эффективное исследование карты"""
    
    def __init__(self):
        self.exploration_grid = {}
        self.frontier = set()
        
    def update_exploration(self, visible_map: List[Dict]):
        """Обновляет данные об исследованной территории"""
        for hex_data in visible_map:
            pos = (hex_data['q'], hex_data['r'])
            self.exploration_grid[pos] = hex_data
            
            # Добавляем соседей в границу исследования
            for neighbor in self.get_neighbors(pos):
                if neighbor not in self.exploration_grid:
                    self.frontier.add(neighbor)
    
    def get_exploration_targets(self, scout_count: int) -> List[Tuple[int, int]]:
        """Возвращает приоритетные цели для исследования"""
        if not self.frontier:
            return []
            
        # Приоритизируем цели по расстоянию от известной территории
        frontier_list = list(self.frontier)
        
        # Простая эвристика - выбираем равномерно распределенные цели
        targets = []
        min_distance = 5  # Минимальное расстояние между целями
        
        for target in frontier_list:
            if not targets:
                targets.append(target)
                continue
                
            # Проверяем, что цель достаточно далеко от уже выбранных
            too_close = False
            for existing_target in targets:
                if self.hex_distance(target, existing_target) < min_distance:
                    too_close = True
                    break
                    
            if not too_close:
                targets.append(target)
                
            if len(targets) >= scout_count:
                break
                
        return targets
    
    @staticmethod
    def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        q, r = pos
        directions = [(+1, 0), (+1, -1), (0, -1), (-1, 0), (-1, +1), (0, +1)]
        return [(q + dq, r + dr) for dq, dr in directions]
    
    @staticmethod
    def hex_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        q1, r1 = pos1
        q2, r2 = pos2
        return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2
