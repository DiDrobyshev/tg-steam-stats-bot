# database.py
import sqlite3
from contextlib import contextmanager
from player_config import load_players
import logging

logger = logging.getLogger(__name__)
DATABASE = 'steam_bot.db'

@contextmanager
def db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        yield cursor
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.commit()
        conn.close()

def init_db():
    """Инициализирует БД и добавляет игроков из конфига"""
    with db_connection() as cursor:
        # Таблица настроек
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        ''')

        # Таблица игроков
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            steam_id TEXT PRIMARY KEY,
            display_name TEXT,
            last_game_id TEXT,
            last_game_name TEXT,
            last_status TEXT,
            total_playtime INTEGER DEFAULT 0
        )
        ''')

        # Таблица сообщений бота
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER,
            message_id INTEGER,
            message_type TEXT CHECK(message_type IN ('main_board', 'notification'))
        )
        ''')

        # Добавляем игроков из конфига
        players = load_players()
        for player in players:
            steam_id = player['steam_id']
            display_name = player['display_name']
            
            cursor.execute(
                "INSERT OR IGNORE INTO players (steam_id, display_name) VALUES (?, ?)",
                (steam_id, display_name)
            )

def save_chat_id(chat_id):
    """Сохраняет chat_id в базе данных"""
    with db_connection() as cursor:
        cursor.execute("DELETE FROM settings WHERE key = 'chat_id'")
        cursor.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)",
            ('chat_id', str(chat_id))
        )
    logger.info(f"Chat ID saved: {chat_id}")

def get_chat_id():
    """Получает сохраненный chat_id из базы данных"""
    with db_connection() as cursor:
        cursor.execute(
            "SELECT value FROM settings WHERE key = 'chat_id'"
        )
        result = cursor.fetchone()
        return int(result['value']) if result else None

def update_player_status(steam_id, game_id, game_name, status):
    """Обновляет статус игрока в БД"""
    with db_connection() as cursor:
        cursor.execute('''
        UPDATE players 
        SET last_game_id = ?, last_game_name = ?, last_status = ?
        WHERE steam_id = ?
        ''', (game_id, game_name, status, steam_id))

def get_last_game(steam_id):
    """Возвращает последнюю игру игрока из БД"""
    with db_connection() as cursor:
        cursor.execute(
            "SELECT last_game_name FROM players WHERE steam_id = ?",
            (steam_id,)
        )
        result = cursor.fetchone()
        return result['last_game_name'] if result else None

def get_main_message_id():
    """Возвращает ID главного сообщения-табло"""
    with db_connection() as cursor:
        cursor.execute(
            "SELECT message_id FROM messages WHERE message_type = 'main_board'"
        )
        result = cursor.fetchone()
        return result['message_id'] if result else None

def set_main_message_id(message_id, chat_id):
    """Устанавливает ID главного сообщения-табло"""
    with db_connection() as cursor:
        # Удаляем старую запись если есть
        cursor.execute(
            "DELETE FROM messages WHERE message_type = 'main_board'"
        )
        # Добавляем новую
        cursor.execute(
            "INSERT INTO messages (message_type, chat_id, message_id) VALUES (?, ?, ?)",
            ('main_board', chat_id, message_id)
        )