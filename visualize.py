import os, time, requests
from dotenv import load_dotenv
from colorama import Fore, Back, Style, init

init(autoreset=True)
load_dotenv()

TOKEN = os.getenv("TOKEN")
HEADERS = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": TOKEN}
BASE_URL = "https://games-test.datsteam.dev/api"  # или боевой

HEX_COLORS = {
    1: Back.MAGENTA, 2: Back.WHITE, 3: Back.YELLOW, 4: Back.RED, 5: Back.BLACK
}
UNIT_CHARS = {0: Fore.YELLOW + "W", 1: Fore.RED + "A", 2: Fore.GREEN + "S"}
ENEMY_CHAR = Fore.MAGENTA + "E"
RESOURCE_CHARS = {1: Fore.CYAN + "a", 2: Fore.CYAN + "b", 3: Fore.CYAN + "n"}

def fetch_arena_data():
    try:
        r = requests.get(f"{BASE_URL}/arena", headers=HEADERS)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("Ошибка:", e)
        return None

def render(arena):
    hexes = {(h['q'], h['r']): h for h in arena.get('map', [])}
    ants = {(a['q'], a['r']): UNIT_CHARS.get(a['type'], '?') for a in arena.get('ants', [])}
    enemies = {(e['q'], e['r']): ENEMY_CHAR for e in arena.get('enemies', [])}
    food = {(f['q'], f['r']): RESOURCE_CHARS.get(f['type'], '?') for f in arena.get('food', [])}

    all_coords = set(hexes) | set(ants) | set(enemies) | set(food)
    qs = [q for q, r in all_coords]
    rs = [r for q, r in all_coords]
    min_q, max_q = min(qs), max(qs)
    min_r, max_r = min(rs), max(rs)

    print(f"\nХОД #{arena.get('turnNo', '?')}")
    for r in range(min_r - 1, max_r + 2):
        line = " " * (max_r - r)
        for q in range(min_q - 1, max_q + 2):
            pos = (q, r)
            bg = HEX_COLORS.get(hexes.get(pos, {}).get('type'), Back.WHITE)
            ch = "."
            if pos in food: ch = food[pos]
            if pos in ants: ch = ants[pos]
            if pos in enemies: ch = enemies[pos]
            line += f"{bg}{ch}{Style.RESET_ALL} "
        print(line)

def loop():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        arena = fetch_arena_data()
        if arena:
            render(arena)
        time.sleep(1.5)

if __name__ == "__main__":
    loop()
