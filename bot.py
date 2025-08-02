import os
import sys
import asyncio
import logging
import re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from config import BOT_TOKEN, ALLOWED_USERS, POINTS_WINNER, POINTS_SCORE, POINTS_BOTH
from database import Database
from football_api import FootballAPI
import fcntl
import atexit
import signal

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
SELECTING_MATCH, SELECTING_WINNER, ENTERING_SCORE = range(3)

class FootballBetBot:
    def __init__(self):
        self.db = Database()
        self.football_api = FootballAPI()
        self.user_states = {}  # Для хранения состояния пользователей
        
        # Файл блокировки для предотвращения дубликатов
        self.lock_file = "/tmp/football_bot.lock"
        self.lock_fd = None
        
    def acquire_lock(self):
        """Приобрести блокировку для предотвращения запуска дубликатов"""
        try:
            self.lock_fd = open(self.lock_file, 'w')
            fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            logging.info("Блокировка приобретена успешно")
            return True
        except (IOError, OSError) as e:
            logging.error(f"Не удалось приобрести блокировку: {e}")
            return False
            
    def release_lock(self):
        """Освободить блокировку"""
        if self.lock_fd:
            try:
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
                self.lock_fd.close()
                if os.path.exists(self.lock_file):
                    os.unlink(self.lock_file)
                logging.info("Блокировка освобождена")
            except Exception as e:
                logging.error(f"Ошибка при освобождении блокировки: {e}")
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        logging.info(f"Получен сигнал {signum}, завершаем работу...")
        self.release_lock()
        sys.exit(0)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user_id = update.effective_user.id
        
        # Проверяем доступ только если список ALLOWED_USERS не пустой
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            await update.message.reply_text("⛔ Доступ запрещен. Бот предназначен только для определенных пользователей.")
            return
        
        # Добавляем пользователя в базу данных
        user = update.effective_user
        self.db.add_user(user.id, user.first_name, user.username or "")
        
        welcome_text = f"""
🤖 **Добро пожаловать в Football Bet Bot!**

Привет, {user.first_name}! Я помогу тебе делать ставки на матчи Real Madrid и Barcelona.

**📋 Доступные команды:**
/calendar - 10 ближайших матчей
/next - Ближайший матч
/bet - Сделать ставку (10 ближайших)
/standings - Таблица результатов
/help - Справка

**🏆 Система баллов:**
• 1 балл за угаданного победителя
• 3 балла за угаданный точный счет
• 4 балла за угаданные и победителя, и счет

Начни с команды /calendar чтобы увидеть ближайшие матчи!
        """
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        user_id = update.effective_user.id
        
        # Проверяем доступ только если список ALLOWED_USERS не пустой
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            return
        
        help_text = """
🤖 **Football Bet Bot - Справка**

📋 **Доступные команды:**
• `/start` - Начать работу с ботом
• `/calendar` - Календарь ближайших матчей
• `/next` - Ближайший матч
• `/last_results` - Последние результаты матчей
• `/bet` - Сделать ставку
• `/standings` - Таблица результатов
• `/stats` - Статистика базы данных
• `/save_data` - Сохранить данные (для админов)
• `/add_demo_results` - Добавить демо-результаты (для админов)
• `/help` - Эта справка

🎯 **Правила начисления баллов:**
• 1 балл за угаданного победителя
• 3 балла за угаданный точный счет
• 4 балла за угаданные и победителя, и счет

⚽ **Поддерживаемые команды:**
• Реал Мадрид
• Барселона

💾 **Сохранение данных:** Данные автоматически сохраняются в Railway Variables

Удачных ставок! 🍀
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stats - статистика базы данных"""
        user_id = update.effective_user.id
        
        # Проверяем доступ только если список ALLOWED_USERS не пустой
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            return
        
        # Получаем статистику
        total_users = len(self.db.users)
        total_matches = len(self.db.matches)
        total_bets = len(self.db.bets)
        
        # Подсчитываем завершенные матчи
        finished_matches = sum(1 for match in self.db.matches.values() if match['status'] == 'finished')
        
        # Подсчитываем общие баллы
        total_points = sum(bet['points'] for bet in self.db.bets.values())
        
        stats_text = f"""
📊 **Статистика базы данных:**

👥 **Пользователи:** {total_users}
⚽ **Матчи:** {total_matches} (завершено: {finished_matches})
💰 **Ставки:** {total_bets}
🏆 **Общие баллы:** {total_points}

📁 **Файл данных:** `bot_data.json`
🔄 **Последнее обновление:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    async def matches(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /matches"""
        user_id = update.effective_user.id
        
        # Проверяем доступ только если список ALLOWED_USERS не пустой
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            return
        
        await update.message.reply_text("🔍 Получаю список матчей...")
        
        # Получаем матчи из API
        matches = self.football_api.get_real_barcelona_matches()
        
        if not matches:
            await update.message.reply_text("❌ Не удалось получить список матчей. Попробуйте позже.")
            return
        
        # Сохраняем матчи в базу данных
        for match in matches:
            match_info = self.football_api.format_match_info(match)
            self.db.add_match(
                match_info['id'],
                match_info['home_team'],
                match_info['away_team'],
                match_info['match_date'],
                match_info['tournament']
            )
        
        # Формируем сообщение со списком матчей
        matches_text = "📅 **Предстоящие матчи Real Madrid vs Barcelona:**\n\n"
        
        for i, match in enumerate(matches, 1):
            match_info = self.football_api.format_match_info(match)
            matches_text += f"{i}. **{match_info['home_team']} vs {match_info['away_team']}**\n"
            matches_text += f"   📅 {match_info['formatted_date']}\n"
            matches_text += f"   🏆 {match_info['tournament']}\n\n"
        
        matches_text += "Используйте /bet для размещения ставки на любой из этих матчей!"
        
        await update.message.reply_text(matches_text, parse_mode='Markdown')
    
    async def calendar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /calendar - показывает 10 ближайших матчей"""
        user_id = update.effective_user.id
        
        # Проверяем доступ только если список ALLOWED_USERS не пустой
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            return
        
        try:
            # Получаем 10 ближайших матчей
            matches = self.football_api.get_next_matches(10)
            
            if not matches:
                await update.message.reply_text("❌ Не удалось получить матчи.")
                return
            
            # Формируем текст
            calendar_text = "📅 **10 ближайших матчей:**\n\n"
            
            for i, match in enumerate(matches, 1):
                home_team = match['homeTeam']['name']
                away_team = match['awayTeam']['name']
                match_date = datetime.fromisoformat(match['utcDate'].replace('Z', '+00:00'))
                formatted_date = match_date.strftime('%d.%m.%Y %H:%M')
                competition = match['competition']['name']
                
                # Добавляем эмодзи для команд
                if 'Real Madrid' in home_team or 'Real Madrid' in away_team:
                    team_emoji = "⚪"
                elif 'Barcelona' in home_team or 'Barcelona' in away_team:
                    team_emoji = "🔵"
                else:
                    team_emoji = "⚽"
                
                calendar_text += f"{i}. {team_emoji} **{home_team} vs {away_team}**\n"
                calendar_text += f"   📅 {formatted_date} | 🏆 {competition}\n\n"
            
            await update.message.reply_text(calendar_text, parse_mode='Markdown')
            
        except Exception as e:
            print(f"Ошибка при получении календаря: {e}")
            await update.message.reply_text("❌ Произошла ошибка при получении календаря.")
    
    async def next_match(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /next - показывает ближайший матч"""
        user_id = update.effective_user.id
        
        # Проверяем доступ только если список ALLOWED_USERS не пустой
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            return
        
        try:
            # Получаем ближайший матч
            match = self.football_api.get_nearest_match()
            
            if not match:
                await update.message.reply_text("❌ Не удалось получить ближайший матч.")
                return
            
            # Формируем информацию о матче
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            match_date = datetime.fromisoformat(match['utcDate'].replace('Z', '+00:00'))
            formatted_date = match_date.strftime('%d.%m.%Y %H:%M')
            competition = match['competition']['name']
            
            # Вычисляем время до матча
            now = datetime.now(match_date.tzinfo)
            time_until = match_date - now
            
            if time_until.days > 0:
                time_text = f"через {time_until.days} дней"
            elif time_until.seconds > 3600:
                hours = time_until.seconds // 3600
                time_text = f"через {hours} часов"
            else:
                minutes = time_until.seconds // 60
                time_text = f"через {minutes} минут"
            
            next_match_text = f"""
⚽ **БЛИЖАЙШИЙ МАТЧ**

🏟️ **{home_team} vs {away_team}**
📅 **Дата:** {formatted_date}
⏰ **До матча:** {time_text}
🏆 **Турнир:** {competition}

🎯 Готовы сделать ставку? Используйте /bet!
            """
            
            await update.message.reply_text(next_match_text, parse_mode='Markdown')
            
        except Exception as e:
            print(f"Ошибка при получении ближайшего матча: {e}")
            await update.message.reply_text("❌ Произошла ошибка при получении ближайшего матча.")
    
    async def last_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /last_results - показывает последние 5 матчей с результатами"""
        user_id = update.effective_user.id
        
        # Проверяем доступ только если список ALLOWED_USERS не пустой
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            return
        
        try:
            # Получаем последние 5 завершенных матчей
            results = self.db.get_last_results(5)
            
            if not results:
                await update.message.reply_text("📊 Пока нет завершенных матчей с результатами.")
                return
            
            # Формируем текст с результатами
            results_text = "🏆 **ПОСЛЕДНИЕ РЕЗУЛЬТАТЫ МАТЧЕЙ**\n\n"
            
            for i, match in enumerate(results, 1):
                home_team = match['home_team']
                away_team = match['away_team']
                home_score = match['home_score']
                away_score = match['away_score']
                match_date = datetime.fromisoformat(match['match_date'])
                formatted_date = match_date.strftime('%d.%m.%Y')
                competition = match['competition']
                
                # Определяем эмодзи для команд
                home_emoji = "⚪" if "Real Madrid" in home_team else "🔵" if "Barcelona" in home_team else "⚽"
                away_emoji = "⚪" if "Real Madrid" in away_team else "🔵" if "Barcelona" in away_team else "⚽"
                
                # Определяем результат
                if home_score > away_score:
                    result_emoji = "🏆"
                    result_text = f"Победа {home_team}"
                elif away_score > home_score:
                    result_emoji = "🏆"
                    result_text = f"Победа {away_team}"
                else:
                    result_emoji = "🤝"
                    result_text = "Ничья"
                
                results_text += f"{i}. {home_emoji} **{home_team}** {home_score}:{away_score} **{away_team}** {away_emoji}\n"
                results_text += f"   {result_emoji} {result_text}\n"
                results_text += f"   📅 {formatted_date} | 🏆 {competition}\n\n"
            
            await update.message.reply_text(results_text, parse_mode='Markdown')
            
        except Exception as e:
            print(f"Ошибка при получении последних результатов: {e}")
            await update.message.reply_text("❌ Произошла ошибка при получении результатов.")
    
    async def add_demo_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавление демо-результатов для тестирования"""
        user_id = update.effective_user.id
        
        # Проверяем доступ только если список ALLOWED_USERS не пустой
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            return
        
        try:
            # Добавляем демо-матчи с результатами
            demo_matches = [
                {
                    'id': 1001,
                    'home_team': 'Real Madrid',
                    'away_team': 'Barcelona',
                    'home_score': 2,
                    'away_score': 1,
                    'match_date': '2025-01-15T20:00:00',
                    'competition': 'La Liga',
                    'status': 'finished'
                },
                {
                    'id': 1002,
                    'home_team': 'Barcelona',
                    'away_team': 'Real Madrid',
                    'home_score': 1,
                    'away_score': 1,
                    'match_date': '2025-01-20T21:00:00',
                    'competition': 'Copa del Rey',
                    'status': 'finished'
                },
                {
                    'id': 1003,
                    'home_team': 'Real Madrid',
                    'away_team': 'Barcelona',
                    'home_score': 3,
                    'away_score': 2,
                    'match_date': '2025-01-25T19:30:00',
                    'competition': 'Champions League',
                    'status': 'finished'
                },
                {
                    'id': 1004,
                    'home_team': 'Barcelona',
                    'away_team': 'Real Madrid',
                    'home_score': 0,
                    'away_score': 2,
                    'match_date': '2025-01-30T20:45:00',
                    'competition': 'La Liga',
                    'status': 'finished'
                },
                {
                    'id': 1005,
                    'home_team': 'Real Madrid',
                    'away_team': 'Barcelona',
                    'home_score': 1,
                    'away_score': 0,
                    'match_date': '2025-02-05T21:15:00',
                    'competition': 'Super Cup',
                    'status': 'finished'
                }
            ]
            
            # Добавляем матчи в базу данных
            for match in demo_matches:
                self.db.matches[str(match['id'])] = match
                self.db._save_data()
            
            await update.message.reply_text("✅ Добавлено 5 демо-результатов матчей! Используйте /last_results для просмотра.")
            
        except Exception as e:
            print(f"Ошибка при добавлении демо-результатов: {e}")
            await update.message.reply_text("❌ Произошла ошибка при добавлении демо-результатов.")
    
    async def save_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ручное сохранение данных в Railway Variables"""
        user_id = update.effective_user.id
        
        # Проверяем доступ только если список ALLOWED_USERS не пустой
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            return
        
        try:
            # Принудительно сохраняем данные
            self.db._save_data()
            
            # Проверяем, что данные сохранились
            total_users = len(self.db.users)
            total_matches = len(self.db.matches)
            total_bets = len(self.db.bets)
            
            await update.message.reply_text(
                f"✅ Данные успешно сохранены!\n\n"
                f"📊 Статистика:\n"
                f"👥 Пользователей: {total_users}\n"
                f"⚽ Матчей: {total_matches}\n"
                f"💰 Ставок: {total_bets}\n\n"
                f"💾 Данные сохранены в Railway Variables"
            )
            
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            await update.message.reply_text("❌ Произошла ошибка при сохранении данных.")
    
    async def bet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /bet - показывает 10 ближайших матчей для ставок"""
        user_id = update.effective_user.id
        
        # Проверяем доступ только если список ALLOWED_USERS не пустой
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            return
        
        try:
            # Получаем 10 ближайших матчей для ставок
            matches = self.football_api.get_upcoming_matches_for_betting(10)
            
            if not matches:
                await update.message.reply_text("❌ Нет доступных матчей для ставок. Попробуйте позже.")
                return
            
            # Создаем клавиатуру с матчами
            keyboard = []
            for match in matches:
                home_team = match['homeTeam']['name']
                away_team = match['awayTeam']['name']
                match_date = datetime.fromisoformat(match['utcDate'].replace('Z', '+00:00'))
                formatted_date = match_date.strftime('%d.%m %H:%M')
                competition = match['competition']['name']
                
                match_text = f"{home_team} vs {away_team} - {formatted_date}"
                keyboard.append([InlineKeyboardButton(match_text, callback_data=f"match_{match['id']}")])
            
            keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="cancel")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "⚽ **Выберите матч для ставки (10 ближайших):**",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return SELECTING_MATCH
            
        except Exception as e:
            print(f"Ошибка при получении матчей для ставок: {e}")
            await update.message.reply_text("❌ Произошла ошибка при получении матчей.")
            return ConversationHandler.END
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        # Проверяем доступ только если список ALLOWED_USERS не пустой
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            return
        
        if query.data == "cancel":
            await query.edit_message_text("❌ Ставка отменена.")
            return ConversationHandler.END
        
        if query.data.startswith("match_"):
            match_id = int(query.data.split("_")[1])
            
            # Получаем матч из API данных
            matches = self.football_api.get_upcoming_matches_for_betting(10)
            match = None
            
            for m in matches:
                if m['id'] == match_id:
                    match = m
                    break
            
            if not match:
                await query.edit_message_text("❌ Матч не найден.")
                return ConversationHandler.END
            
            # Сохраняем выбранный матч в контексте
            context.user_data['selected_match'] = match
            
            # Создаем клавиатуру для выбора победителя
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            
            keyboard = [
                [InlineKeyboardButton(f"🏠 {home_team} (Домашняя)", callback_data="winner_home")],
                [InlineKeyboardButton("🤝 Ничья", callback_data="winner_draw")],
                [InlineKeyboardButton(f"✈️ {away_team} (Гостевая)", callback_data="winner_away")],
                [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            match_date = datetime.fromisoformat(match['utcDate'].replace('Z', '+00:00'))
            formatted_date = match_date.strftime('%d.%m.%Y %H:%M')
            competition = match['competition']['name']
            
            await query.edit_message_text(
                f"⚽ **{home_team} vs {away_team}**\n\n"
                f"📅 {formatted_date}\n"
                f"🏆 {competition}\n\n"
                "🎯 **Кто победит?**",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return SELECTING_WINNER
        
        elif query.data.startswith("winner_"):
            winner = query.data.split("_")[1]
            context.user_data['predicted_winner'] = winner
            
            match = context.user_data['selected_match']
            
            await query.edit_message_text(
                f"⚽ **{match['homeTeam']['name']} vs {match['awayTeam']['name']}**\n\n"
                f"🎯 Победитель: {self._get_winner_text(winner, match)}\n\n"
                "📊 **Введите предполагаемый счет (например: 2:1):**",
                parse_mode='Markdown'
            )
            
            return ENTERING_SCORE
    
    def _get_winner_text(self, winner, match):
        """Получение текстового представления победителя"""
        if winner == 'home':
            return f"🏠 {match['homeTeam']['name']}"
        elif winner == 'away':
            return f"✈️ {match['awayTeam']['name']}"
        else:
            return "🤝 Ничья"
    
    async def handle_score_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ввода счета"""
        user_id = update.effective_user.id
        
        # Проверяем доступ только если список ALLOWED_USERS не пустой
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            return ConversationHandler.END
        
        score_text = update.message.text.strip()
        
        # Проверяем формат счета
        if not re.match(r'^\d+:\d+$', score_text):
            await update.message.reply_text(
                "❌ Неверный формат счета. Используйте формат X:Y (например: 2:1)"
            )
            return ENTERING_SCORE
        
        home_score, away_score = map(int, score_text.split(':'))
        
        if home_score < 0 or away_score < 0:
            await update.message.reply_text("❌ Счет не может быть отрицательным.")
            return ENTERING_SCORE
        
        # Сохраняем ставку в базу данных
        match = context.user_data['selected_match']
        predicted_winner = context.user_data['predicted_winner']
        
        # Сначала сохраняем матч в базу данных, если его там нет
        self.db.add_match(
            match['id'],
            match['homeTeam']['name'],
            match['awayTeam']['name'],
            match['utcDate'],
            match['competition']['name']
        )
        
        bet_id = self.db.add_bet(
            user_id,
            match['id'],
            predicted_winner,
            home_score,
            away_score
        )
        
        # Формируем подтверждение ставки
        match_date = datetime.fromisoformat(match['utcDate'].replace('Z', '+00:00'))
        formatted_date = match_date.strftime('%d.%m.%Y %H:%M')
        
        confirmation_text = f"""
✅ **Ставка размещена успешно!**

⚽ **Матч:** {match['homeTeam']['name']} vs {match['awayTeam']['name']}
📅 **Дата:** {formatted_date}
🏆 **Турнир:** {match['competition']['name']}

🎯 **Ваш прогноз:**
• Победитель: {self._get_winner_text(predicted_winner, match)}
• Счет: {home_score}:{away_score}

💰 **Возможные баллы:**
• 1 балл за угаданного победителя
• 3 балла за угаданный точный счет
• 4 балла за угаданные и победителя, и счет

Используйте /standings для просмотра таблицы результатов!
        """
        
        await update.message.reply_text(confirmation_text, parse_mode='Markdown')
        
        # Очищаем данные пользователя
        context.user_data.clear()
        
        return ConversationHandler.END
    
    async def standings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /standings"""
        user_id = update.effective_user.id
        
        # Проверяем доступ только если список ALLOWED_USERS не пустой
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            return
        
        standings = self.db.get_standings()
        
        if not standings:
            await update.message.reply_text("📊 Пока нет данных для таблицы результатов.")
            return
        
        standings_text = "🏆 **Таблица результатов:**\n\n"
        
        for i, (user_id, username, total_points, correct_winners, correct_scores, total_bets) in enumerate(standings, 1):
            display_name = username or f"Пользователь {user_id}"
            
            standings_text += f"{i}. **{display_name}**\n"
            standings_text += f"   📊 Всего баллов: {total_points}\n"
            standings_text += f"   ✅ Угаданных победителей: {correct_winners}\n"
            standings_text += f"   🎯 Угаданных счетов: {correct_scores}\n"
            standings_text += f"   📝 Всего ставок: {total_bets}\n\n"
        
        await update.message.reply_text(standings_text, parse_mode='Markdown')
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена операции"""
        await update.message.reply_text("❌ Операция отменена.")
        return ConversationHandler.END

def main():
    """Основная функция запуска бота"""
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не установлен в переменных окружения")
        return
    
    bot = FootballBetBot()
    
    # Проверяем блокировку
    if not bot.acquire_lock():
        print("❌ Бот уже запущен. Выход.")
        sys.exit(1)
    
    # Устанавливаем обработчики сигналов
    signal.signal(signal.SIGINT, bot.signal_handler)
    signal.signal(signal.SIGTERM, bot.signal_handler)
    
    # Устанавливаем обработчик для освобождения блокировки при завершении
    atexit.register(bot.release_lock)
    
    # Инициализируем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("matches", bot.matches))
    application.add_handler(CommandHandler("calendar", bot.calendar))
    application.add_handler(CommandHandler("next", bot.next_match))
    application.add_handler(CommandHandler("last_results", bot.last_results)) # Добавляем обработчик для последних результатов
    application.add_handler(CommandHandler("stats", bot.stats))
    application.add_handler(CommandHandler("standings", bot.standings))
    application.add_handler(CommandHandler("add_demo_results", bot.add_demo_results)) # Добавляем обработчик для добавления демо-результатов
    application.add_handler(CommandHandler("save_data", bot.save_data)) # Добавляем обработчик для сохранения данных
    
    # Добавляем ConversationHandler для ставок
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("bet", bot.bet)],
        states={
            SELECTING_MATCH: [CallbackQueryHandler(bot.button_handler)],
            SELECTING_WINNER: [CallbackQueryHandler(bot.button_handler)],
            ENTERING_SCORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_score_input)]
        },
        fallbacks=[CommandHandler("cancel", bot.cancel)]
    )
    application.add_handler(conv_handler)
    
    # Запускаем бота
    print("🤖 Football Bet Bot запущен...")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
    finally:
        bot.release_lock()

if __name__ == '__main__':
    main() 