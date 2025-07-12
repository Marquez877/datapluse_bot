"""
Основной игровой бот с интеграцией всех стратегий
"""
import time
import json
from typing import List, Dict
from config import APIclient
from strategy import TacticalFormations, ResourceManager, ThreatAnalyzer, MapExplorer

class GameBot:
    """Главный класс игрового бота"""
    
    def __init__(self, use_test_server=True):
        self.api_client = APIclient(use_test_server=use_test_server)
        self.formations = TacticalFormations()
        self.resource_manager = ResourceManager()
        self.threat_analyzer = ThreatAnalyzer()
        self.map_explorer = MapExplorer()
        
        self.game_state = {
            'current_strategy': 'balanced',
            'turn_count': 0,
            'last_score': 0,
            'performance_metrics': {
                'resources_collected': 0,
                'enemies_killed': 0,
                'ants_lost': 0,
                'territory_explored': 0
            }
        }
        
    def analyze_game_situation(self, arena_data: Dict) -> Dict:
        """Комплексный анализ игровой ситуации"""
        battlefield_analysis = self.threat_analyzer.analyze_battlefield(arena_data)
        
        our_ants = arena_data.get('ants', [])
        ant_composition = {
            'workers': [ant for ant in our_ants if ant['type'] == 0],
            'fighters': [ant for ant in our_ants if ant['type'] == 1],
            'scouts': [ant for ant in our_ants if ant['type'] == 2]
        }
        
        situation = {
            'battlefield': battlefield_analysis,
            'ant_composition': ant_composition,
            'resource_situation': len(arena_data.get('food', [])),
            'exploration_progress': len(self.map_explorer.exploration_grid),
            'immediate_threats': len([e for e in arena_data.get('enemies', []) 
                                    if self.api_client.hex_distance(
                                        (e['q'], e['r']), 
                                        (arena_data['home'][0]['q'], arena_data['home'][0]['r'])
                                    ) <= 5])
        }
        
        return situation
    
    def decide_strategy(self, situation: Dict) -> str:
        """Принятие стратегического решения"""
        battlefield = situation['battlefield']
        composition = situation['ant_composition']
        
        # Анализируем текущую ситуацию
        total_ants = len(composition['workers']) + len(composition['fighters']) + len(composition['scouts'])
        fighter_ratio = len(composition['fighters']) / max(total_ants, 1)
        
        immediate_threats = situation['immediate_threats']
        
        # Логика выбора стратегии
        if immediate_threats > 3 or battlefield['recommended_strategy'] == 'defensive':
            return 'defensive'
        elif (battlefield['our_strength'] > battlefield['enemy_strength'] * 1.3 and 
              fighter_ratio > 0.3):
            return 'aggressive'
        elif situation['resource_situation'] > 10 and len(composition['workers']) < total_ants * 0.5:
            return 'economic'
        else:
            return 'balanced'
    
    def execute_defensive_strategy(self, arena_data: Dict, situation: Dict):
        """Выполнение оборонительной стратегии"""
        moves = []
        composition = situation['ant_composition']
        home_coords = arena_data.get('home', [])
        
        # Формируем оборону
        if composition['fighters']:
            defensive_positions = self.formations.create_defensive_formation(
                composition['fighters'], home_coords
            )
            
            for fighter in composition['fighters']:
                if fighter['id'] in defensive_positions:
                    target = defensive_positions[fighter['id']]
                    path = self.api_client.find_path_astar(
                        (fighter['q'], fighter['r']), target, arena_data
                    )
                    if len(path) > 1:
                        moves.append({
                            "ant": fighter['id'],
                            "path": path[1:]
                        })
        
        # Рабочие прячутся и собирают ресурсы рядом с домом
        safe_resources = []
        for food in arena_data.get('food', []):
            food_pos = (food['q'], food['r'])
            home_distance = min(self.api_client.hex_distance(
                food_pos, (h['q'], h['r'])
            ) for h in home_coords)
            
            if home_distance <= 5:  # Только близкие ресурсы
                safe_resources.append(food)
        
        worker_assignments = self.resource_manager.assign_resources(
            composition['workers'], safe_resources, home_coords
        )
        
        for worker in composition['workers']:
            if worker.get('food') and worker['food'].get('amount', 0) > 0:
                # Идем домой
                closest_home = min(home_coords, 
                                 key=lambda h: self.api_client.hex_distance(
                                     (worker['q'], worker['r']), (h['q'], h['r'])
                                 ))
                path = self.api_client.find_path_astar(
                    (worker['q'], worker['r']), 
                    (closest_home['q'], closest_home['r']), 
                    arena_data
                )
            elif worker['id'] in worker_assignments:
                target = worker_assignments[worker['id']]
                path = self.api_client.find_path_astar(
                    (worker['q'], worker['r']), target, arena_data
                )
            else:
                # Прячемся у дома
                path = self.api_client.find_path_astar(
                    (worker['q'], worker['r']), 
                    (home_coords[0]['q'], home_coords[0]['r']), 
                    arena_data
                )
            
            if len(path) > 1:
                moves.append({
                    "ant": worker['id'],
                    "path": path[1:]
                })
        
        return moves
    
    def execute_aggressive_strategy(self, arena_data: Dict, situation: Dict):
        """Выполнение агрессивной стратегии"""
        moves = []
        composition = situation['ant_composition']
        enemies = arena_data.get('enemies', [])
        
        if not enemies:
            return self.execute_balanced_strategy(arena_data, situation)
        
        # Группируем бойцов для атаки
        priority_targets = []
        for enemy in enemies:
            priority = {0: 3, 1: 1, 2: 2}.get(enemy['type'], 1)  # Рабочие приоритетнее
            priority_targets.append((enemy, priority))
        
        priority_targets.sort(key=lambda x: x[1], reverse=True)
        
        if priority_targets and composition['fighters']:
            main_target = priority_targets[0][0]
            target_pos = (main_target['q'], main_target['r'])
            
            attack_positions = self.formations.create_attack_formation(
                composition['fighters'], target_pos
            )
            
            for fighter in composition['fighters']:
                if fighter['id'] in attack_positions:
                    attack_pos = attack_positions[fighter['id']]
                    path = self.api_client.find_path_astar(
                        (fighter['q'], fighter['r']), attack_pos, arena_data
                    )
                    if len(path) > 1:
                        moves.append({
                            "ant": fighter['id'],
                            "path": path[1:]
                        })
        
        # Рабочие продолжают собирать ресурсы, но осторожно
        worker_moves = self.plan_worker_moves(composition['workers'], arena_data)
        moves.extend(worker_moves)
        
        # Разведчики ищут врагов
        scout_moves = self.plan_scout_moves(composition['scouts'], arena_data, aggressive=True)
        moves.extend(scout_moves)
        
        return moves
    
    def execute_economic_strategy(self, arena_data: Dict, situation: Dict):
        """Выполнение экономической стратегии"""
        moves = []
        composition = situation['ant_composition']
        
        # Максимизируем сбор ресурсов
        all_resources = arena_data.get('food', [])
        worker_assignments = self.resource_manager.assign_resources(
            composition['workers'], all_resources, arena_data.get('home', [])
        )
        
        worker_moves = self.plan_worker_moves(composition['workers'], arena_data, worker_assignments)
        moves.extend(worker_moves)
        
        # Минимальная оборона
        if composition['fighters']:
            home_coords = arena_data.get('home', [])
            defensive_positions = self.formations.create_defensive_formation(
                composition['fighters'][:2], home_coords  # Только часть бойцов
            )
            
            for fighter in composition['fighters'][:2]:
                if fighter['id'] in defensive_positions:
                    target = defensive_positions[fighter['id']]
                    path = self.api_client.find_path_astar(
                        (fighter['q'], fighter['r']), target, arena_data
                    )
                    if len(path) > 1:
                        moves.append({
                            "ant": fighter['id'],
                            "path": path[1:]
                        })
        
        # Активная разведка для поиска ресурсов
        scout_moves = self.plan_scout_moves(composition['scouts'], arena_data, resource_focus=True)
        moves.extend(scout_moves)
        
        return moves
    
    def execute_balanced_strategy(self, arena_data: Dict, situation: Dict):
        """Выполнение сбалансированной стратегии"""
        moves = []
        composition = situation['ant_composition']
        
        # Рабочие собирают ресурсы
        worker_moves = self.plan_worker_moves(composition['workers'], arena_data)
        moves.extend(worker_moves)
        
        # Бойцы патрулируют
        fighter_moves = self.plan_fighter_moves(composition['fighters'], arena_data)
        moves.extend(fighter_moves)
        
        # Разведчики исследуют
        scout_moves = self.plan_scout_moves(composition['scouts'], arena_data)
        moves.extend(scout_moves)
        
        return moves
    
    def plan_worker_moves(self, workers: List[Dict], arena_data: Dict, 
                         assignments: Dict = None) -> List[Dict]:
        """Планирование движения рабочих"""
        moves = []
        
        if assignments is None:
            assignments = self.resource_manager.assign_resources(
                workers, arena_data.get('food', []), arena_data.get('home', [])
            )
        
        for worker in workers:
            path = self.api_client.plan_worker_move(
                worker, arena_data.get('food', []), 
                arena_data.get('home', []), arena_data
            )
            
            if len(path) > 1:
                moves.append({
                    "ant": worker['id'],
                    "path": path[1:]
                })
        
        return moves
    
    def plan_fighter_moves(self, fighters: List[Dict], arena_data: Dict) -> List[Dict]:
        """Планирование движения бойцов"""
        moves = []
        
        for fighter in fighters:
            path = self.api_client.plan_fighter_move(
                fighter, arena_data.get('enemies', []), 
                arena_data, arena_data.get('ants', [])
            )
            
            if len(path) > 1:
                moves.append({
                    "ant": fighter['id'],
                    "path": path[1:]
                })
        
        return moves
    
    def plan_scout_moves(self, scouts: List[Dict], arena_data: Dict, 
                        aggressive: bool = False, resource_focus: bool = False) -> List[Dict]:
        """Планирование движения разведчиков"""
        moves = []
        
        self.map_explorer.update_exploration(arena_data.get('map', []))
        exploration_targets = self.map_explorer.get_exploration_targets(len(scouts))
        
        for i, scout in enumerate(scouts):
            if i < len(exploration_targets):
                target = exploration_targets[i]
                path = self.api_client.find_path_astar(
                    (scout['q'], scout['r']), target, arena_data
                )
            else:
                path = self.api_client.plan_scout_move(scout, arena_data)
            
            if len(path) > 1:
                moves.append({
                    "ant": scout['id'],
                    "path": path[1:]
                })
        
        return moves
    
    def execute_turn(self):
        """Выполнение хода с использованием всех стратегий"""
        arena_data = self.api_client.get_arena()
        if not arena_data:
            return False
        
        self.game_state['turn_count'] += 1
        
        # Анализируем ситуацию
        situation = self.analyze_game_situation(arena_data)
        
        # Принимаем стратегическое решение
        new_strategy = self.decide_strategy(situation)
        if new_strategy != self.game_state['current_strategy']:
            print(f"Смена стратегии: {self.game_state['current_strategy']} -> {new_strategy}")
            self.game_state['current_strategy'] = new_strategy
        
        # Выполняем выбранную стратегию
        if new_strategy == 'defensive':
            moves = self.execute_defensive_strategy(arena_data, situation)
        elif new_strategy == 'aggressive':
            moves = self.execute_aggressive_strategy(arena_data, situation)
        elif new_strategy == 'economic':
            moves = self.execute_economic_strategy(arena_data, situation)
        else:
            moves = self.execute_balanced_strategy(arena_data, situation)
        
        # Отправляем команды
        if moves:
            result = self.api_client.send_move(moves)
            if result is None:
                return False
        
        # Обновляем метрики
        current_score = arena_data.get('score', 0)
        if current_score > self.game_state['last_score']:
            self.game_state['performance_metrics']['resources_collected'] += current_score - self.game_state['last_score']
        self.game_state['last_score'] = current_score
        
        # Выводим статистику
        print(f"Ход {self.game_state['turn_count']}: {new_strategy} стратегия")
        print(f"Отправлено команд: {len(moves)}")
        print(f"Счет: {current_score}")
        print(f"Муравьев: {len(arena_data.get('ants', []))}")
        print(f"Враги: {len(arena_data.get('enemies', []))}")
        print(f"Ресурсы: {len(arena_data.get('food', []))}")
        print("-" * 50)
        
        return True
    
    def run_game_loop(self):
        """Основной игровой цикл"""
        print("Запуск игрового бота...")
        
        # Регистрируемся на раунд
        registration_result = self.api_client.register_for_round()
        if registration_result:
            print("✓ Успешно зарегистрированы на раунд!")
        else:
            print("✗ Не удалось зарегистрироваться")
            return
        
        # Основной игровой цикл
        try:
            while True:
                arena_data = self.api_client.get_arena()
                if not arena_data:
                    print("Нет данных арены, ожидание...")
                    time.sleep(2)
                    continue
                
                next_turn_in = arena_data.get('nextTurnIn', 0)
                if next_turn_in > 0:
                    if not self.execute_turn():
                        print("Ошибка выполнения хода")
                        break
                    
                    # Ждем до следующего хода
                    sleep_time = min(next_turn_in - 0.5, 2.0)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                else:
                    print("Раунд завершен!")
                    break
                    
        except KeyboardInterrupt:
            print("\nОстановлено пользователем")
        except Exception as e:
            print(f"Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
        
        # Финальная статистика
        print("\n" + "="*50)
        print("ФИНАЛЬНАЯ СТАТИСТИКА:")
        print(f"Ходов сыграно: {self.game_state['turn_count']}")
        print(f"Финальный счет: {self.game_state['last_score']}")
        print(f"Ресурсов собрано: {self.game_state['performance_metrics']['resources_collected']}")
        print("="*50)

if __name__ == "__main__":
    bot = GameBot()
    bot.run_game_loop()
