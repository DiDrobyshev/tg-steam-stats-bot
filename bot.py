# bot.py
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from database import init_db, save_chat_id
from scheduler import SchedulerManager
from player_config import load_players
import os

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start и /start@имябота"""
    # Получаем информацию о чате
    chat = update.effective_chat
    
    # Сохраняем chat_id в базу данных
    save_chat_id(chat.id)
    logger.info(f"Chat ID saved: {chat.id} (title: {chat.title})")
    
    players = load_players()
    player_list = "\n".join([f"- {p['display_name']} ({p['steam_id']})" for p in players])
    
    response = (
        "🚀 Бот активирован!\n\n"
        f"Чат ID: `{chat.id}`\n"
        f"Тип чата: {'группа' if chat.type in ['group', 'supergroup'] else 'личный'}\n\n"
        f"Отслеживаемые игроки:\n{player_list}\n\n"
        "Статус будет обновляться автоматически каждые 10 минут."
    )
    
    await context.bot.send_message(
        chat_id=chat.id,
        text=response,
        parse_mode="Markdown"
    )

async def reload_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принудительно перезагружает список игроков"""
    from player_config import load_players
    load_players(force_reload=True)
    
    players = load_players()
    player_list = "\n".join([f"- {p['display_name']} ({p['steam_id']})" for p in players])
    
    await update.message.reply_text(
        "✅ Список игроков успешно перезагружен!\n\n"
        f"Текущие игроки ({len(players)}):\n{player_list}",
        parse_mode="Markdown"
    )

def main():
    """Запуск бота"""
    # Инициализация базы данных
    init_db()
    logger.info("Database initialized")
    
    # Создаем Application
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reload", reload_players))  # Добавлена команда /reload
    
    # Инициализируем и запускаем планировщик
    scheduler = SchedulerManager(application)
    scheduler.start()
    
    # Запускаем бота
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == '__main__':
    main()