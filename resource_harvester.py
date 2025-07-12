#!/usr/bin/env python3
"""
🔥 АСИНХРОННАЯ СИСТЕМА МАССОВОГО СБОРА РЕСУРСОВ
Команда MACAN team: максимальная эффективность!
"""

import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import time
from config import TOKEN, HEADERS

class ResourceHarvester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = None
        self.resource_targets = {}
        self.harvest_efficiency = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def async_get_arena(self):
        """Асинхронное получение данных арены"""
        try:
            async with self.session.get(
                f"{self.base_url}/arena", 
                headers=HEADERS,
                timeout=aiohttp.ClientTimeout(total=2)
            ) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"Ошибка async_get_arena: {e}")
        return None
    
    async def async_send_moves(self, moves):
        """Асинхронная отправка команд"""
        try:
            async with self.session.post(
                f"{self.base_url}/move",
                headers=HEADERS,
                json={"moves": moves},
                timeout=aiohttp.ClientTimeout(total=2)
            ) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"Ошибка async_send_moves: {e}")
        return None
    
    def calculate_harvest_efficiency(self, workers, visible_food):
        """Расчет эффективности сбора ресурсов"""
        if not workers or not visible_food:
            return 0
            
        total_food_value = sum(
            food.get('amount', 1) * self.get_food_value(food.get('type', 1))
            for food in visible_food
        )
        
        worker_capacity = len(workers) * 8  # Грузоподъемность рабочего
        
        return min(100, (total_food_value / max(1, worker_capacity)) * 100)
    
    def get_food_value(self, food_type):
        """Ценность ресурса"""
        return {1: 10, 2: 20, 3: 60}.get(food_type, 10)  # яблоко, хлеб, нектар
    
    async def optimize_resource_collection(self, arena_data):
        """Оптимизация сбора ресурсов"""
        workers = [ant for ant in arena_data.get('ants', []) if ant['type'] == 0]
        visible_food = arena_data.get('food', [])
        
        if not workers:
            return []
        
        # Сортируем ресурсы по ценности
        sorted_food = sorted(visible_food, 
                           key=lambda f: (self.get_food_value(f.get('type', 1)) * f.get('amount', 1)), 
                           reverse=True)
        
        assignments = []
        used_workers = set()
        
        for food in sorted_food:
            if len(used_workers) >= len(workers):
                break
                
            food_pos = (food['q'], food['r'])
            
            # Находим ближайшего свободного рабочего
            available_workers = [w for w in workers if w['id'] not in used_workers]
            if not available_workers:
                break
                
            closest_worker = min(available_workers, 
                               key=lambda w: abs(w['q'] - food['q']) + abs(w['r'] - food['r']))
            
            assignments.append({
                'worker_id': closest_worker['id'],
                'target': food_pos,
                'value': self.get_food_value(food.get('type', 1)) * food.get('amount', 1)
            })
            
            used_workers.add(closest_worker['id'])
        
        return assignments
