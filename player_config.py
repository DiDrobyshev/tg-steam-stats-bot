# player_config.py
import json
import os
import logging
import time

logger = logging.getLogger(__name__)

# Кэширование списка игроков
LAST_RELOAD_TIME = 0
PLAYERS_CACHE = []
CACHE_DURATION = 300  # 5 минут

def load_players(force_reload=False):
    global LAST_RELOAD_TIME, PLAYERS_CACHE
    
    # Перезагружаем если:
    # - принудительно
    # - кэш устарел
    # - кэш пустой
    if force_reload or time.time() - LAST_RELOAD_TIME > CACHE_DURATION or not PLAYERS_CACHE:
        try:
            if not os.path.exists('players.json'):
                logger.error("Файл players.json не найден!")
                return []
                
            with open('players.json', 'r', encoding='utf-8') as f:
                PLAYERS_CACHE = json.load(f)
                LAST_RELOAD_TIME = time.time()
                logger.info("Список игроков перезагружен")
                
        except json.JSONDecodeError:
            logger.exception("Ошибка формата players.json!")
        except Exception as e:
            logger.exception(f"Ошибка загрузки players.json: {str(e)}")
    
    return PLAYERS_CACHE

def get_player_ids():
    return [player['steam_id'] for player in load_players()]

def get_player_name(steam_id):
    for player in load_players():
        if player['steam_id'] == steam_id:
            return player['display_name']
    return f"Игрок {steam_id}"