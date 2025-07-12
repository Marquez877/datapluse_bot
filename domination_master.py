#!/usr/bin/env python3
"""
🎯 МАСТЕР-СИСТЕМА ИНТЕГРАЦИИ: ПОЛНОЕ ДОМИНИРОВАНИЕ
Команда MACAN team - объединяем все модули для максимальной эффективности!
"""

import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import APIclient
from ultra_aggressive import UltraAggressiveStrategy
from resource_harvester import ResourceHarvester
from zone_controller import ZoneController
from rhythm_controller import GameRhythmController, DecisionMaker

class DominationMaster:
    def __init__(self, base_url="https://games-test.datsteam.dev"):
        self.base_url = base_url
        self.api_client = APIclient(base_url)
        self.ultra_strategy = UltraAggressiveStrategy()
        self.zone_controller = ZoneController()
        self.rhythm_controller = GameRhythmController()
        self.decision_maker = DecisionMaker()
        
        # Состояние системы
        self.total_moves_made = 0
        self.successful_moves = 0
        self.game_phase = "early"  # early, mid, late
        self.performance_metrics = {
            'ant_growth_rate': 0,
            'resource_efficiency': 0,
            'territory_control': 0,
            'combat_effectiveness': 0
        }
        
        # Многопоточность
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.processing_lock = threading.Lock()
        
    async def run_domination_cycle(self):
        """ГЛАВНЫЙ ЦИКЛ ДОМИНИРОВАНИЯ"""
        print("🔥 ЗАПУСК СИСТЕМЫ ПОЛНОГО ДОМИНИРОВАНИЯ! 🔥")
        
        async with ResourceHarvester(self.base_url) as harvester:
            turn_count = 0
            
            while True:
                turn_start = time.time()
                print(f"\n=== ХОД {turn_count + 1} ===")
                
                try:
                    # Получаем данные арены
                    arena_data = await harvester.async_get_arena()
                    if not arena_data:
                        await asyncio.sleep(0.5)
                        continue
                    
                    # Анализ игровой фазы
                    self.update_game_phase(arena_data)
                    
                    # Параллельный анализ всех систем
                    analysis_tasks = await self.parallel_analysis(arena_data, harvester)
                    
                    # Принятие мастер-решения
                    master_plan = self.create_master_plan(analysis_tasks, arena_data)
                    
                    # Выполнение плана
                    execution_result = await self.execute_master_plan(master_plan, harvester)
                    
                    # Обновление метрик
                    self.update_performance_metrics(arena_data, execution_result)
                    
                    # Адаптация стратегии
                    self.adapt_strategy()
                    
                    # Контроль темпа
                    turn_duration = time.time() - turn_start
                    self.rhythm_controller.record_turn_metrics(
                        turn_start, 
                        len(master_plan.get('actions', [])),
                        execution_result.get('successful_actions', 0)
                    )
                    
                    # Отчет о прогрессе
                    self.print_progress_report(arena_data, turn_count)
                    
                    turn_count += 1
                    
                    # Оптимальная задержка
                    optimal_delay = self.rhythm_controller.optimize_turn_timing()
                    await asyncio.sleep(optimal_delay)
                    
                except Exception as e:
                    print(f"❌ Ошибка в цикле доминирования: {e}")
                    await asyncio.sleep(1)
    
    async def parallel_analysis(self, arena_data, harvester):
        """Параллельный анализ всех систем"""
        analysis_results = {}
        
        # Запускаем анализ параллельно
        tasks = {
            'ultra_strategy': asyncio.create_task(
                self.analyze_ultra_strategy(arena_data)
            ),
            'resource_optimization': asyncio.create_task(
                harvester.optimize_resource_collection(arena_data)
            ),
            'territory_analysis': asyncio.create_task(
                self.analyze_territory(arena_data)
            ),
            'rhythm_analysis': asyncio.create_task(
                self.analyze_rhythm()
            )
        }
        
        # Собираем результаты
        for name, task in tasks.items():
            try:
                analysis_results[name] = await task
            except Exception as e:
                print(f"⚠️ Ошибка анализа {name}: {e}")
                analysis_results[name] = {}
        
        return analysis_results
    
    async def analyze_ultra_strategy(self, arena_data):
        """Анализ ультра-агрессивной стратегии"""
        return await asyncio.get_event_loop().run_in_executor(
            self.executor,
            self.ultra_strategy.analyze_situation,
            arena_data
        )
    
    async def analyze_territory(self, arena_data):
        """Анализ территории"""
        return await asyncio.get_event_loop().run_in_executor(
            self.executor,
            self.zone_controller.analyze_territory,
            arena_data
        )
    
    async def analyze_rhythm(self):
        """Анализ ритма игры"""
        return await asyncio.get_event_loop().run_in_executor(
            self.executor,
            self.rhythm_controller.analyze_game_tempo
        )
    
    def create_master_plan(self, analysis_results, arena_data):
        """Создание мастер-плана действий"""
        ants = arena_data.get('ants', [])
        
        # Базовые данные
        workers = [ant for ant in ants if ant['type'] == 0]
        fighters = [ant for ant in ants if ant['type'] == 1]
        scouts = [ant for ant in ants if ant['type'] == 2]
        
        master_plan = {
            'actions': [],
            'priorities': [],
            'emergency_actions': []
        }
        
        # Приоритет 1: Создание муравьев (если возможно)
        if len(ants) < 50:  # Лимит роста
            create_ant_action = self.plan_ant_creation(arena_data)
            if create_ant_action:
                master_plan['actions'].append(create_ant_action)
        
        # Приоритет 2: Сбор ресурсов
        resource_assignments = analysis_results.get('resource_optimization', [])
        for assignment in resource_assignments[:10]:  # Топ-10 заданий
            master_plan['actions'].append({
                'type': 'move',
                'ant_id': assignment['worker_id'],
                'target': assignment['target'],
                'priority': 90
            })
        
        # Приоритет 3: Территориальное расширение
        expansion_zones = analysis_results.get('territory_analysis', [])
        for i, (zone_pos, score) in enumerate(expansion_zones[:3]):
            if scouts and i < len(scouts):
                master_plan['actions'].append({
                    'type': 'move',
                    'ant_id': scouts[i]['id'],
                    'target': zone_pos,
                    'priority': 70
                })
        
        # Приоритет 4: Ультра-агрессивные действия
        ultra_actions = analysis_results.get('ultra_strategy', {}).get('actions', [])
        master_plan['actions'].extend(ultra_actions[:5])
        
        return master_plan
    
    def plan_ant_creation(self, arena_data):
        """Планирование создания муравья"""
        ants = arena_data.get('ants', [])
        nectar = arena_data.get('nectar', 0)
        
        if nectar < 10:  # Недостаточно нектара
            return None
        
        # Определяем тип муравья для создания
        workers = len([ant for ant in ants if ant['type'] == 0])
        fighters = len([ant for ant in ants if ant['type'] == 1])
        scouts = len([ant for ant in ants if ant['type'] == 2])
        
        total_ants = len(ants)
        
        # Оптимальный состав
        optimal_composition = self.zone_controller.calculate_optimal_composition(total_ants + 1)
        
        # Выбираем тип для создания
        if workers < optimal_composition['workers']:
            ant_type = 0  # Рабочий
        elif fighters < optimal_composition['fighters']:
            ant_type = 1  # Боец
        else:
            ant_type = 2  # Разведчик
        
        return {
            'type': 'create_ant',
            'ant_type': ant_type,
            'priority': 100
        }
    
    async def execute_master_plan(self, master_plan, harvester):
        """Выполнение мастер-плана"""
        actions = master_plan.get('actions', [])
        if not actions:
            return {'successful_actions': 0}
        
        # Сортируем по приоритету
        actions.sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        # Формируем команды для API
        moves = []
        for action in actions[:20]:  # Лимит на количество действий
            if action['type'] == 'move':
                moves.append({
                    'ant_id': action['ant_id'],
                    'q': action['target'][0],
                    'r': action['target'][1]
                })
            elif action['type'] == 'create_ant':
                moves.append({
                    'create': True,
                    'type': action['ant_type']
                })
        
        # Отправляем команды
        if moves:
            result = await harvester.async_send_moves(moves)
            self.total_moves_made += len(moves)
            
            if result:
                self.successful_moves += len(moves)
                return {'successful_actions': len(moves)}
        
        return {'successful_actions': 0}
    
    def update_game_phase(self, arena_data):
        """Обновление игровой фазы"""
        ants = arena_data.get('ants', [])
        ant_count = len(ants)
        
        if ant_count < 10:
            self.game_phase = "early"
        elif ant_count < 30:
            self.game_phase = "mid"
        else:
            self.game_phase = "late"
    
    def update_performance_metrics(self, arena_data, execution_result):
        """Обновление метрик производительности"""
        ants = arena_data.get('ants', [])
        
        # Скорость роста армии
        current_ant_count = len(ants)
        self.performance_metrics['ant_growth_rate'] = current_ant_count
        
        # Эффективность выполнения
        if self.total_moves_made > 0:
            self.performance_metrics['execution_efficiency'] = (
                self.successful_moves / self.total_moves_made * 100
            )
    
    def adapt_strategy(self):
        """Адаптация стратегии"""
        tempo_analysis = self.rhythm_controller.analyze_game_tempo()
        
        if tempo_analysis.get('recommended_mode') == 'ultra_aggressive':
            self.ultra_strategy.aggressiveness_level = min(1.0, 
                self.ultra_strategy.aggressiveness_level + 0.1)
        elif tempo_analysis.get('avg_efficiency', 0) < 50:
            self.ultra_strategy.aggressiveness_level = max(0.3, 
                self.ultra_strategy.aggressiveness_level - 0.1)
    
    def print_progress_report(self, arena_data, turn_count):
        """Отчет о прогрессе"""
        ants = arena_data.get('ants', [])
        nectar = arena_data.get('nectar', 0)
        
        workers = len([ant for ant in ants if ant['type'] == 0])
        fighters = len([ant for ant in ants if ant['type'] == 1])
        scouts = len([ant for ant in ants if ant['type'] == 2])
        
        efficiency = 0
        if self.total_moves_made > 0:
            efficiency = (self.successful_moves / self.total_moves_made) * 100
        
        print(f"🏆 ПРОГРЕСС ДОМИНИРОВАНИЯ:")
        print(f"   📊 Ход: {turn_count + 1}")
        print(f"   🐜 Муравьи: {len(ants)} (Р:{workers}, Б:{fighters}, Р:{scouts})")
        print(f"   🍯 Нектар: {nectar}")
        print(f"   📈 Эффективность: {efficiency:.1f}%")
        print(f"   🎯 Фаза: {self.game_phase}")

# Точка входа
async def main():
    """ГЛАВНАЯ ФУНКЦИЯ ЗАПУСКА"""
    master = DominationMaster()
    await master.run_domination_cycle()

if __name__ == "__main__":
    print("🚀 СИСТЕМА ПОЛНОГО ДОМИНИРОВАНИЯ АКТИВИРОВАНА!")
    print("🏆 Команда MACAN team готова к победе!")
    asyncio.run(main())
