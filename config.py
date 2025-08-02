import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# Разрешенные пользователи (Telegram ID)
# Убрали ограничения - теперь любой пользователь может использовать бота
ALLOWED_USERS = []  # Пустой список означает доступ для всех

# API для футбольных данных
# Получите бесплатный ключ на https://www.football-data.org/
FOOTBALL_API_KEY = "2e2ce24f4bf442b5bcb6bc35d920070b"  # Ваш API ключ
FOOTBALL_API_BASE_URL = 'https://api.football-data.org/v4'

# Команды Real Madrid и Barcelona
REAL_MADRID_ID = 86  # ID Real Madrid в API
BARCELONA_ID = 81    # ID Barcelona в API

# Система баллов
POINTS_WINNER = 1     # Балл за угаданного победителя
POINTS_SCORE = 3      # Баллы за угаданный счет
POINTS_BOTH = 4       # Баллы за угаданные и победителя, и счет

# Настройки базы данных
DATABASE_PATH = 'football_bets.db'

# Настройки уведомлений
NOTIFICATION_BEFORE_MATCH = 60  # минуты до матча 