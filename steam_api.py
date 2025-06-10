# steam_api.py
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

STEAM_API_KEY = os.getenv('STEAM_API_KEY')

def get_player_summary(steam_id):
    try:
        url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={steam_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('response', {}).get('players'):
            return {
                'steam_id': steam_id,
                'name': f"Игрок {steam_id} (не найден)",
                'status': 'offline',
                'game_id': None,
                'game_name': None,
                'last_online': datetime.now()
            }
            
        player = data['response']['players'][0]
        return {
            'steam_id': steam_id,
            'name': player.get('personaname', f"Игрок {steam_id}"),
            'status': 'offline' if player.get('personastate', 0) == 0 else 'online',
            'game_id': player.get('gameid'),
            'game_name': player.get('gameextrainfo'),
            'last_online': datetime.fromtimestamp(player.get('lastlogoff', 0))
        }
    except Exception as e:
        logger.error(f"Steam API error for {steam_id}: {str(e)}")
        return {
            'steam_id': steam_id,
            'name': f"Игрок {steam_id} (ошибка)",
            'status': 'error',
            'game_id': None,
            'game_name': None,
            'last_online': datetime.now()
        }