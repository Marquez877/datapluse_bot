#!/usr/bin/env python3
"""
🚀 СИСТЕМА УПРАВЛЕНИЯ РИТМОМ И ТЕМПОМ ИГРЫ
Команда MACAN team: контролируем темп битвы!
"""

import time
from collections import deque
import statistics

class GameRhythmController:
    def __init__(self):
        self.turn_times = deque(maxlen=20)  # Последние 20 ходов
        self.response_times = deque(maxlen=20)
        self.action_efficiency = deque(maxlen=20)
        self.tempo_mode = "aggressive"  # aggressive, balanced, defensive
        
    def record_turn_metrics(self, turn_start_time, actions_taken, successful_actions):
        """Записать метрики хода"""
        turn_duration = time.time() - turn_start_time
        self.turn_times.append(turn_duration)
        
        efficiency = (successful_actions / max(1, actions_taken)) * 100
        self.action_efficiency.append(efficiency)
        
    def analyze_game_tempo(self):
        """Анализ темпа игры"""
        if len(self.turn_times) < 3:
            return {"status": "insufficient_data"}
        
        avg_turn_time = statistics.mean(self.turn_times)
        avg_efficiency = statistics.mean(self.action_efficiency)
        
        # Анализ тренда
        recent_times = list(self.turn_times)[-5:]
        early_times = list(self.turn_times)[:5] if len(self.turn_times) >= 10 else recent_times
        
        tempo_trend = "stable"
        if len(recent_times) >= 3 and len(early_times) >= 3:
            if statistics.mean(recent_times) < statistics.mean(early_times):
                tempo_trend = "accelerating"
            elif statistics.mean(recent_times) > statistics.mean(early_times):
                tempo_trend = "slowing"
        
        return {
            "avg_turn_time": avg_turn_time,
            "avg_efficiency": avg_efficiency,
            "tempo_trend": tempo_trend,
            "recommended_mode": self.recommend_tempo_mode(avg_efficiency, tempo_trend)
        }
    
    def recommend_tempo_mode(self, efficiency, trend):
        """Рекомендация режима темпа"""
        if efficiency > 80 and trend == "accelerating":
            return "ultra_aggressive"
        elif efficiency > 60:
            return "aggressive"
        elif efficiency > 40:
            return "balanced"
        else:
            return "conservative"
    
    def calculate_action_priority(self, action_type, current_situation):
        """Расчет приоритета действия"""
        base_priorities = {
            "create_ant": 100,
            "collect_resource": 90,
            "move_to_food": 85,
            "explore": 70,
            "attack": 60,
            "defend": 80
        }
        
        priority = base_priorities.get(action_type, 50)
        
        # Модификация в зависимости от режима
        if self.tempo_mode == "ultra_aggressive":
            if action_type in ["create_ant", "collect_resource"]:
                priority += 20
        elif self.tempo_mode == "aggressive":
            if action_type in ["create_ant", "collect_resource", "move_to_food"]:
                priority += 10
        elif self.tempo_mode == "conservative":
            if action_type == "defend":
                priority += 15
        
        # Модификация в зависимости от ситуации
        ant_count = current_situation.get('ant_count', 0)
        if ant_count < 10 and action_type == "create_ant":
            priority += 30  # Критически важно наращивать армию
        
        return min(150, priority)  # Максимум 150
    
    def optimize_turn_timing(self):
        """Оптимизация времени хода"""
        if not self.turn_times:
            return 0.3  # Базовая задержка
        
        avg_time = statistics.mean(self.turn_times)
        
        # Адаптивная задержка
        if avg_time < 0.2:  # Слишком быстро
            return 0.4
        elif avg_time > 1.0:  # Слишком медленно
            return 0.1
        else:
            return max(0.1, min(0.5, avg_time * 0.8))
    
    def emergency_tempo_boost(self, crisis_level):
        """Экстренное ускорение темпа"""
        boost_settings = {
            "low": {"delay_reduction": 0.7, "action_limit": 15},
            "medium": {"delay_reduction": 0.5, "action_limit": 20},
            "high": {"delay_reduction": 0.3, "action_limit": 25},
            "critical": {"delay_reduction": 0.1, "action_limit": 30}
        }
        
        return boost_settings.get(crisis_level, boost_settings["low"])

class DecisionMaker:
    def __init__(self):
        self.decision_history = deque(maxlen=50)
        self.success_rate = {}
        
    def make_strategic_decision(self, options, current_state):
        """Принятие стратегического решения"""
        scored_options = []
        
        for option in options:
            score = self.evaluate_option(option, current_state)
            scored_options.append((option, score))
        
        # Сортировка по убыванию очков
        scored_options.sort(key=lambda x: x[1], reverse=True)
        
        # Выбор лучшего варианта с элементом случайности
        if len(scored_options) > 1:
            top_options = scored_options[:min(3, len(scored_options))]
            weights = [opt[1] for opt in top_options]
            
            # Взвешенный выбор
            total_weight = sum(weights)
            if total_weight > 0:
                import random
                choice_value = random.uniform(0, total_weight)
                current_weight = 0
                
                for option, weight in top_options:
                    current_weight += weight
                    if choice_value <= current_weight:
                        return option
        
        return scored_options[0][0] if scored_options else options[0]
    
    def evaluate_option(self, option, state):
        """Оценка варианта действия"""
        base_score = option.get('base_score', 50)
        
        # Исторический успех
        option_type = option.get('type', 'unknown')
        historical_success = self.success_rate.get(option_type, 0.5)
        
        # Текущая ситуация
        urgency_bonus = option.get('urgency', 0) * 10
        resource_bonus = option.get('resource_value', 0)
        risk_penalty = option.get('risk_level', 0) * 5
        
        total_score = (
            base_score + 
            historical_success * 20 + 
            urgency_bonus + 
            resource_bonus - 
            risk_penalty
        )
        
        return max(0, total_score)
    
    def update_success_rate(self, option_type, was_successful):
        """Обновление статистики успеха"""
        current_rate = self.success_rate.get(option_type, 0.5)
        # Экспоненциальное сглаживание
        alpha = 0.1
        new_rate = alpha * (1.0 if was_successful else 0.0) + (1 - alpha) * current_rate
        self.success_rate[option_type] = new_rate
