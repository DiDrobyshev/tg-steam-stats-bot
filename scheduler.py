# scheduler.py
import logging
from database import update_player_status, get_last_game, get_main_message_id, set_main_message_id, get_chat_id
from steam_api import get_player_summary
from message_formatter import format_main_board, format_game_notification
from player_config import get_player_ids, get_player_name, load_players
import os
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class SchedulerManager:
    def __init__(self, application):
        self.application = application
        self.bot = application.bot
        self.player_ids = get_player_ids()
        self.player_status_cache = {}
        self.job_queue = application.job_queue
        
    def start(self):
        """Запускает периодические задачи"""
        # Обновление табло каждые 10 минут
        self.job_queue.run_repeating(
            self.update_main_board,  # ИСПРАВЛЕНО: update_main_board (с "a")
            interval=600,  # 10 минут в секундах
            first=10
        )
        
        # Проверка изменений статуса каждую минуту
        self.job_queue.run_repeating(
            self.check_game_changes,
            interval=60,   # 1 минута в секундах
            first=5
        )
        logger.info("Scheduler tasks registered")
        
    async def update_main_board(self, context: ContextTypes.DEFAULT_TYPE):  # ИСПРАВЛЕНО: update_main_board (с "a")
        """Обновляет основное табло"""
        # Принудительно обновляем кэш игроков
        load_players()
        
        logger.info("Updating main board...")
        players_data = []
        player_ids = get_player_ids()
        
        for steam_id in player_ids:
            try:
                summary = get_player_summary(steam_id)
                display_name = get_player_name(steam_id)
                
                # Обработка различных состояний
                if summary.get('status') == 'error':
                    player_data = {
                        'steam_id': steam_id,
                        'name': display_name,
                        'status': 'error',
                        'is_playing': False,
                        'current_game': "Ошибка получения данных"
                    }
                elif summary.get('game_name'):
                    player_data = {
                        'steam_id': steam_id,
                        'name': display_name,
                        'status': summary['status'],
                        'is_playing': True,
                        'current_game': summary['game_name']
                    }
                else:
                    player_data = {
                        'steam_id': steam_id,
                        'name': display_name,
                        'status': summary['status'],
                        'is_playing': False,
                        'current_game': None
                    }
                
                players_data.append(player_data)
            except Exception as e:
                logger.error(f"Ошибка обработки игрока {steam_id}: {str(e)}")
                players_data.append({
                    'steam_id': steam_id,
                    'name': get_player_name(steam_id),
                    'status': 'error',
                    'is_playing': False,
                    'current_game': "Критическая ошибка"
                })
        
        message_text = format_main_board(players_data)
        await self.update_main_message(message_text)
        
    async def check_game_changes(self, context: ContextTypes.DEFAULT_TYPE):
        """Проверяет изменения статуса игры"""
        logger.debug("Checking game changes...")
        
        for steam_id in self.player_ids:
            summary = get_player_summary(steam_id)
            if not summary:
                continue
                
            current_game_id = summary.get('game_id')
            current_game_name = summary.get('game_name')
            display_name = get_player_name(steam_id)
            
            prev_status = self.player_status_cache.get(steam_id, {})
            current_status = {
                'game_id': current_game_id,
                'game_name': current_game_name,
                'status': summary['status']
            }
            
            if prev_status != current_status:
                logger.info(f"Status changed for {display_name}: {prev_status} -> {current_status}")
                self.player_status_cache[steam_id] = current_status
                
                await self.send_game_notification(
                    steam_id, 
                    display_name,
                    prev_status.get('game_name'),
                    current_game_name
                )
                
                update_player_status(
                    steam_id,
                    current_game_id,
                    current_game_name,
                    summary['status']
                )
    
    async def send_game_notification(self, steam_id, player_name, prev_game, current_game):
        """Отправляет уведомление о смене игры"""
        if current_game:
            message = format_game_notification(player_name, current_game, True)
            await self.send_message(message)
        elif prev_game:
            last_game = get_last_game(steam_id) or prev_game
            message = format_game_notification(player_name, last_game, False)
            await self.send_message(message)
    
    async def update_main_message(self, text):
        """Обновляет главное сообщение-табло"""
        # Получаем chat_id из базы данных
        chat_id = get_chat_id()
        
        if not chat_id:
            logger.error("Chat ID not configured! Use /start command in target chat first.")
            return
            
        message_id = get_main_message_id()
        
        try:
            if message_id:
                await self.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=text,
                    parse_mode="Markdown"
                )
                logger.info("Main board message updated")
            else:
                message = await self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode="Markdown"
                )
                set_main_message_id(message.message_id, chat_id)
                logger.info("New main board message created")
                
        except Exception as e:
            logger.error(f"Error updating main message: {e}")
            message = await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="Markdown"
            )
            set_main_message_id(message.message_id, chat_id)
            logger.info("Created new main board after error")
    
    async def send_message(self, text):
        """Отправляет обычное сообщение в чат"""
        try:
            chat_id = get_chat_id()
            if not chat_id:
                logger.error("Cannot send notification: Chat ID not set")
                return
                
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error sending message: {e}")