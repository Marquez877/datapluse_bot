#!/usr/bin/env python3
"""
🔍 ДИАГНОСТИКА СОЗДАНИЯ МУРАВЬЕВ
Команда MACAN team: Эрмек Озгонбеков, Элдияр Адылбеков, Каныкей Ашыракманова
"""

from config import APIclient

def diagnose_ant_creation():
    """Диагностика проблем с созданием муравьев"""
    
    print("🔍 ДИАГНОСТИКА СОЗДАНИЯ МУРАВЬЕВ")
    print("=" * 50)
    
    client = APIclient(use_test_server=True)
    arena_data = client.get_arena()
    
    if not arena_data:
        print("❌ Не удалось получить данные арены")
        return
    
    ants = arena_data.get('ants', [])
    home_coords = arena_data.get('home', [])
    spot = arena_data.get('spot', {})
    
    print(f"📊 ТЕКУЩАЯ СИТУАЦИЯ:")
    print(f"Наших муравьев: {len(ants)}")
    print(f"Ход №: {arena_data.get('turnNo', 0)}")
    print(f"Счет: {arena_data.get('score', 0)}")
    
    print(f"\n🏠 МУРАВЕЙНИК:")
    print(f"Координаты дома: {home_coords}")
    print(f"Основной гекс (spot): {spot}")
    
    # Анализируем позиции муравьев
    print(f"\n🐜 АНАЛИЗ МУРАВЬЕВ:")
    main_hex = (spot.get('q', 0), spot.get('r', 0))
    types_on_main = []
    
    for i, ant in enumerate(ants):
        ant_pos = (ant['q'], ant['r'])
        ant_type = ant['type']
        type_name = {0: 'Рабочий', 1: 'Боец', 2: 'Разведчик'}.get(ant_type, 'Неизвестный')
        
        print(f"  {i+1}. {type_name} на ({ant['q']}, {ant['r']})")
        print(f"     Здоровье: {ant['health']}")
        
        if ant.get('food'):
            print(f"     Несет ресурс: тип {ant['food'].get('type')}, кол-во {ant['food'].get('amount')}")
        
        # Проверяем, стоит ли на основном гексе
        if ant_pos == main_hex:
            print(f"     ⚠️  СТОИТ НА ОСНОВНОМ ГЕКСЕ! Блокирует создание {type_name}")
            types_on_main.append(type_name)
    
    print(f"\n🚨 ПРОБЛЕМЫ С СОЗДАНИЕМ:")
    if types_on_main:
        print(f"❌ На основном гексе стоят: {', '.join(types_on_main)}")
        print("   Это блокирует создание новых муравьев такого же типа!")
        print("   РЕШЕНИЕ: переместите их с основного гекса")
    else:
        print("✅ Основной гекс свободен - муравьи должны создаваться")
    
    # Проверяем лимиты
    print(f"\n📈 ЛИМИТЫ:")
    print(f"Текущее количество: {len(ants)}/100")
    if len(ants) >= 100:
        print("❌ ДОСТИГНУТ ЛИМИТ 100 МУРАВЬЕВ!")
    else:
        print(f"✅ Место есть: можно создать еще {100 - len(ants)} муравьев")
    
    # Статистика по типам
    worker_count = sum(1 for ant in ants if ant['type'] == 0)
    fighter_count = sum(1 for ant in ants if ant['type'] == 1) 
    scout_count = sum(1 for ant in ants if ant['type'] == 2)
    
    print(f"\n📊 СТАТИСТИКА ПО ТИПАМ:")
    print(f"Рабочие: {worker_count} (должно быть ~60%)")
    print(f"Бойцы: {fighter_count} (должно быть ~30%)")
    print(f"Разведчики: {scout_count} (должно быть ~10%)")
    
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    if types_on_main:
        print("1. Переместите муравьев с основного гекса")
        print("2. Основной гекс должен быть всегда свободен")
    if len(ants) < 10:
        print("3. У вас мало муравьев - проверьте, не погибают ли они")
        print("4. Избегайте кислотных гексов")
        print("5. Держитесь подальше от врагов")
    
    return arena_data

if __name__ == "__main__":
    diagnose_ant_creation()
