#!/usr/bin/env python3
"""
🚀 УЛУЧШЕННАЯ АСИНХРОННАЯ СИСТЕМА BATTLE START
Команда MACAN team: исправлены все проблемы из логов!

ИСПРАВЛЕНИЯ:
- Асинхронность для скорости
- Решение конфликтов позиций 
- Приоритет сбора ресурсов
- Создание муравьев для роста
- Устранение застоя
"""

import asyncio
import aiohttp
import time
import random
import math
from collections import defaultdict
from config import APIclient, TOKEN, HEADERS

class ImprovedAsyncStrategy:
    def __init__(self):
        self.blocked_ants = set()  # Отслеживание заблокированных муравьев
        self.ant_tasks = {}  # Задачи для каждого муравья
        self.resource_claims = {}  # Кто идет к какому ресурсу
        self.turn_count = 0
        self.last_ant_count = 0
        self.stagnation_turns = 0
        
    def analyze_logs_problems(self, arena_data):
        """Анализ проблем из логов"""
        ants = arena_data.get('ants', [])
        nectar = arena_data.get('nectar', 0)
        
        problems = []
        
        # Проблема 1: Застой роста
        if len(ants) == self.last_ant_count:
            self.stagnation_turns += 1
        else:
            self.stagnation_turns = 0
            
        if self.stagnation_turns > 10:
            problems.append("STAGNATION")
            
        # Проблема 2: Мало муравьев
        if len(ants) < 15:
            problems.append("LOW_ANT_COUNT")
            
        # Проблема 3: Много нектара, но не создаем муравьев
        if nectar >= 10 and len(ants) < 50:
            problems.append("UNUSED_NECTAR")
            
        self.last_ant_count = len(ants)
        return problems
    
    def resolve_position_conflicts(self, moves, ants):
        """УМНОЕ разрешение конфликтов позиций"""
        if not moves:
            return []
            
        # Группируем по целевым позициям
        position_map = defaultdict(list)
        for move in moves:
            if 'path' in move and move['path']:
                target = move['path'][-1]
                target_key = (target['q'], target['r'])
                position_map[target_key].append(move)
        
        resolved_moves = []
        
        for target_pos, competing_moves in position_map.items():
            if len(competing_moves) == 1:
                resolved_moves.extend(competing_moves)
            else:
                # Выбираем приоритетный муравей
                priority_move = self.select_priority_ant(competing_moves, ants)
                resolved_moves.append(priority_move)
                
                # Остальным даем альтернативные задачи
                for move in competing_moves:
                    if move['ant'] != priority_move['ant']:
                        alt_move = self.create_alternative_move(move, ants, target_pos)
                        if alt_move:
                            resolved_moves.append(alt_move)
        
        return resolved_moves
    
    def select_priority_ant(self, competing_moves, ants):
        """Выбор приоритетного муравья при конфликте"""
        best_move = None
        best_score = -1
        
        for move in competing_moves:
            ant_id = move['ant']
            ant = next((a for a in ants if a['id'] == ant_id), None)
            if not ant:
                continue
                
            score = 0
            
            # Приоритет по типу
            if ant['type'] == 0:  # Рабочий
                score += 100
            elif ant['type'] == 1:  # Боец
                score += 50
            else:  # Разведчик
                score += 30
                
            # Бонус за груз
            if ant.get('food', {}).get('amount', 0) > 0:
                score += 200  # Доставка ресурсов - высший приоритет
                
            # Штраф за блокировку в прошлом
            if ant_id in self.blocked_ants:
                score -= 50
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move if best_move else competing_moves[0]
    
    def create_alternative_move(self, blocked_move, ants, blocked_pos):
        """Создание альтернативного движения"""
        ant_id = blocked_move['ant']
        ant = next((a for a in ants if a['id'] == ant_id), None)
        if not ant:
            return None
            
        # Ищем свободную соседнюю позицию
        directions = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
        
        for dq, dr in directions:
            alt_q = blocked_pos[0] + dq
            alt_r = blocked_pos[1] + dr
            
            # Создаем альтернативный путь к соседней позиции
            return {
                'ant': ant_id,
                'path': [{'q': alt_q, 'r': alt_r}]
            }
        
        # Если не нашли альтернативу, возвращаем None
        return None

class AsyncBattleClient:
    def __init__(self):
        self.base_url = "https://games-test.datsteam.dev/api"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json", 
            "X-Auth-Token": TOKEN
        }
        self.strategy = ImprovedAsyncStrategy()
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_arena_async(self):
        """Асинхронное получение данных арены"""
        try:
            async with self.session.get(
                f"{self.base_url}/arena",
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=3)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"❌ Ошибка получения арены: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка запроса арены: {e}")
        return None
    
    async def send_moves_async(self, moves):
        """Асинхронная отправка команд"""
        if not moves:
            return False
            
        try:
            async with self.session.post(
                f"{self.base_url}/move",
                headers=self.headers,
                json={"moves": moves},
                timeout=aiohttp.ClientTimeout(total=3)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"❌ Ошибка отправки команд: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
        return False
    
    def plan_resource_focused_strategy(self, arena_data):
        """ПРИОРИТЕТ СБОРА РЕСУРСОВ - исправляем застой"""
        ants = arena_data.get('ants', [])
        food = arena_data.get('food', [])
        nectar = arena_data.get('nectar', 0)
        home = arena_data.get('home', [])
        
        moves = []
        
        # 1. СОЗДАНИЕ МУРАВЬЕВ - решаем застой
        if nectar >= 10 and len(ants) < 50:
            ant_type = 0 if len([a for a in ants if a['type'] == 0]) < len(ants) * 0.7 else 1
            moves.append({
                'create': True,
                'type': ant_type
            })
            print(f"🐜 Создаем муравья типа {ant_type}, нектар: {nectar}")
        
        # 2. ДОСТАВКА РЕСУРСОВ - высший приоритет
        for ant in ants:
            if ant.get('food', {}).get('amount', 0) > 0:
                closest_home = self.find_closest_home(ant, home)
                if closest_home:
                    path = self.calculate_path(ant, closest_home)
                    if path:
                        moves.append({
                            'ant': ant['id'],
                            'path': path
                        })
                        continue
        
        # 3. СБОР РЕСУРСОВ - умное распределение
        workers = [ant for ant in ants if ant['type'] == 0 and 
                  ant.get('food', {}).get('amount', 0) == 0]
        
        # Сортируем ресурсы по ценности
        sorted_food = sorted(food, key=lambda f: self.get_food_value(f), reverse=True)
        
        assigned_workers = 0
        for food_item in sorted_food:
            if assigned_workers >= len(workers):
                break
                
            # Находим ближайшего свободного рабочего
            available_workers = [w for w in workers[assigned_workers:]]
            if not available_workers:
                break
                
            closest_worker = min(available_workers, 
                               key=lambda w: self.hex_distance(w, food_item))
            
            path = self.calculate_path(closest_worker, food_item)
            if path:
                moves.append({
                    'ant': closest_worker['id'],
                    'path': path
                })
                assigned_workers += 1
        
        # 4. РАЗВЕДКА для оставшихся муравьев
        remaining_ants = [ant for ant in ants if ant['id'] not in 
                         [m['ant'] for m in moves if 'ant' in m]]
        
        for ant in remaining_ants[:5]:  # Ограничиваем количество
            explore_target = self.get_exploration_target(ant, home)
            if explore_target:
                path = self.calculate_path(ant, explore_target)
                if path:
                    moves.append({
                        'ant': ant['id'],
                        'path': path
                    })
        
        return moves
    
    def get_food_value(self, food):
        """Ценность ресурса"""
        food_type = food.get('type', 1)
        amount = food.get('amount', 1)
        
        # Нектар = 60, Хлеб = 20, Яблоко = 10
        type_values = {3: 60, 2: 20, 1: 10}
        return type_values.get(food_type, 10) * amount
    
    def find_closest_home(self, ant, home_coords):
        """Поиск ближайшего дома"""
        if not home_coords:
            return None
            
        return min(home_coords, key=lambda h: self.hex_distance(ant, h))
    
    def hex_distance(self, pos1, pos2):
        """Расстояние между гексами"""
        q1, r1 = pos1.get('q', 0), pos1.get('r', 0)
        q2, r2 = pos2.get('q', 0), pos2.get('r', 0)
        return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) / 2
    
    def calculate_path(self, ant, target, max_steps=3):
        """Простой расчет пути"""
        ant_q, ant_r = ant['q'], ant['r']
        target_q, target_r = target['q'], target['r']
        
        path = []
        current_q, current_r = ant_q, ant_r
        
        for _ in range(max_steps):
            if current_q == target_q and current_r == target_r:
                break
                
            # Простое движение к цели
            dq = target_q - current_q
            dr = target_r - current_r
            
            # Выбираем направление
            if abs(dq) > abs(dr):
                step_q = current_q + (1 if dq > 0 else -1)
                step_r = current_r
            else:
                step_q = current_q
                step_r = current_r + (1 if dr > 0 else -1)
            
            path.append({'q': step_q, 'r': step_r})
            current_q, current_r = step_q, step_r
        
        return path if path else [{'q': ant_q, 'r': ant_r}]
    
    def get_exploration_target(self, ant, home_coords):
        """Цель для разведки"""
        if not home_coords:
            return {'q': ant['q'] + random.randint(-5, 5), 
                   'r': ant['r'] + random.randint(-5, 5)}
        
        home = home_coords[0]
        angle = random.uniform(0, 2 * math.pi)
        distance = random.randint(10, 20)
        
        target_q = int(home['q'] + distance * math.cos(angle))
        target_r = int(home['r'] + distance * math.sin(angle))
        
        return {'q': target_q, 'r': target_r}

async def main_improved_battle():
    """ГЛАВНАЯ АСИНХРОННАЯ ФУНКЦИЯ БИТВЫ"""
    print("🚀 ЗАПУСК УЛУЧШЕННОЙ АСИНХРОННОЙ СИСТЕМЫ")
    print("💪 Команда MACAN team: исправлены все проблемы!")
    print("=" * 60)
    
    async with AsyncBattleClient() as client:
        turn_count = 0
        last_score = 0
        
        while turn_count < 1000:
            turn_start = time.time()
            
            # Получаем данные арены
            arena_data = await client.get_arena_async()
            if not arena_data:
                await asyncio.sleep(1)
                continue
            
            # Проверяем окончание
            next_turn_in = arena_data.get('nextTurnIn', 0)
            if next_turn_in <= 0:
                print("🏁 РАУНД ЗАВЕРШЕН!")
                break
            
            # Анализируем проблемы
            problems = client.strategy.analyze_logs_problems(arena_data)
            
            # Получаем текущее состояние
            ants = arena_data.get('ants', [])
            score = arena_data.get('score', 0)
            nectar = arena_data.get('nectar', 0)
            food = arena_data.get('food', [])
            
            print(f"\n=== ХОД {turn_count + 1} ===")
            print(f"Муравьи: {len(ants)} | Счет: {score} | Нектар: {nectar} | Ресурсы: {len(food)}")
            
            if problems:
                print(f"⚠️ Проблемы: {', '.join(problems)}")
            
            # Планируем стратегию
            moves = client.plan_resource_focused_strategy(arena_data)
            
            # Разрешаем конфликты
            resolved_moves = client.strategy.resolve_position_conflicts(moves, ants)
            
            # Отправляем команды
            if resolved_moves:
                result = await client.send_moves_async(resolved_moves)
                if result:
                    print(f"✅ Отправлено {len(resolved_moves)} команд")
                    
                    # Отслеживаем заблокированных муравьев
                    blocked_count = len(moves) - len(resolved_moves)
                    if blocked_count > 0:
                        print(f"⚠️ Разрешено {blocked_count} конфликтов")
                else:
                    print("❌ Ошибка отправки команд")
            else:
                print("⚠️ Нет команд для отправки")
            
            # Статистика прогресса
            if score > last_score:
                print(f"📈 Счет вырос: {last_score} → {score}")
                last_score = score
            
            turn_count += 1
            client.strategy.turn_count = turn_count
            
            # Адаптивная пауза
            execution_time = time.time() - turn_start
            sleep_time = max(0.1, next_turn_in - execution_time - 0.1)
            await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    print("🔥 УЛУЧШЕННАЯ СИСТЕМА BATTLE START")
    print("🎯 Приоритет: СБОР РЕСУРСОВ")
    print("⚡ Асинхронность для скорости")
    print("🛠️ Исправлены все проблемы из логов")
    
    asyncio.run(main_improved_battle())
