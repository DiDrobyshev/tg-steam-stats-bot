# message_formatter.py
from datetime import datetime

def format_main_board(players_data):
    """Форматирует основное табло со статусами игроков"""
    # Заголовок
    current_time = datetime.now().strftime("%H:%M")
    message = f"🎮 *ИГРОВОЕ ТАБЛО* | Обновлено {current_time}\n"
    message += "━━━━━━━━━━━━━━━━━━\n"
    
    for player in players_data:
        # Иконка статуса
        if player.get('is_playing'):
            status_icon = "🟠"
            status_text = f"В игре: *{player['current_game']}*"
        elif player['status'] == 'online':
            status_icon = "🟢"
            status_text = "В сети"
        else:
            status_icon = "🔴"
            status_text = "Не в сети"
        
        # Блок игрока - только статус и игра
        message += f"{status_icon} *{player['name']}*\n"
        message += f"└─ {status_text}\n\n"
    
    # Футер
    message += "━━━━━━━━━━━━━━━━━━\n"
    message += "Следующее обновление через 10 минут"
    
    return message

def format_game_notification(player_name, game_name, is_start=True):
    """Форматирует уведомление о смене игры"""
    action = "запустил" if is_start else "вышел из"
    return f"🎮 *{player_name}* {action} *{game_name}*"