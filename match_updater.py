import time
import schedule
import sqlite3
from datetime import datetime, timedelta
from database import Database
from football_api import FootballAPI
from config import POINTS_WINNER, POINTS_SCORE, POINTS_BOTH

class MatchUpdater:
    def __init__(self):
        self.db = Database()
        self.football_api = FootballAPI()
    
    def update_finished_matches(self):
        """Обновление результатов завершенных матчей"""
        print(f"🔄 Проверка завершенных матчей... {datetime.now()}")
        
        # Получаем матчи, которые должны были завершиться
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, api_match_id, home_team, away_team, match_date
                FROM matches 
                WHERE status = 'SCHEDULED' 
                AND match_date < datetime('now', '-2 hours')
            ''')
            
            matches_to_update = cursor.fetchall()
        
        for match in matches_to_update:
            match_id, api_match_id, home_team, away_team, match_date = match
            
            print(f"📊 Проверяю матч: {home_team} vs {away_team}")
            
            # Получаем результат из API
            result = self.football_api.get_match_result(api_match_id)
            
            if result:
                # Обновляем результат матча
                self.db.update_match_result(
                    match_id, 
                    result['home_score'], 
                    result['away_score']
                )
                
                print(f"✅ Результат обновлен: {result['home_score']}:{result['away_score']}")
                
                # Рассчитываем баллы для всех ставок на этот матч
                self.calculate_points_for_match(match_id)
            else:
                print(f"❌ Не удалось получить результат для матча {match_id}")
    
    def calculate_points_for_match(self, match_id):
        """Расчет баллов для всех ставок на конкретный матч"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id FROM bets WHERE match_id = ? AND points_earned = 0
            ''', (match_id,))
            
            bets = cursor.fetchall()
        
        for bet in bets:
            bet_id = bet[0]
            points = self.db.calculate_bet_points(bet_id)
            
            if points > 0:
                print(f"🏆 Начислено {points} баллов за ставку {bet_id}")
            else:
                print(f"💔 0 баллов за ставку {bet_id}")
    
    def add_demo_results(self):
        """Добавление демо-результатов для тестирования"""
        print("🎮 Добавление демо-результатов...")
        
        # Получаем демо-матчи
        demo_matches = self.football_api._get_demo_matches()
        
        for i, match in enumerate(demo_matches):
            # Создаем демо-результаты
            if i == 0:  # Первый матч: Real Madrid 2:1 Barcelona
                home_score, away_score = 2, 1
            elif i == 1:  # Второй матч: Barcelona 1:1 Real Madrid
                home_score, away_score = 1, 1
            else:  # Третий матч: Real Madrid 3:2 Barcelona
                home_score, away_score = 3, 2
            
            # Добавляем матч в базу
            match_info = self.football_api.format_match_info(match)
            db_match_id = self.db.add_match(
                match_info['id'],
                match_info['home_team'],
                match_info['away_team'],
                match_info['match_date'],
                match_info['tournament']
            )
            
            # Устанавливаем результат
            self.db.update_match_result(db_match_id, home_score, away_score)
            
            print(f"🎯 Демо-результат: {match_info['home_team']} {home_score}:{away_score} {match_info['away_team']}")
    
    def run_scheduler(self):
        """Запуск планировщика обновлений"""
        print("⏰ Запуск планировщика обновлений матчей...")
        
        # Обновляем результаты каждые 30 минут
        schedule.every(30).minutes.do(self.update_finished_matches)
        
        # Обновляем сразу при запуске
        self.update_finished_matches()
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Проверяем каждую минуту

def main():
    """Основная функция для запуска обновления матчей"""
    updater = MatchUpdater()
    
    # Добавляем демо-результаты для тестирования
    updater.add_demo_results()
    
    # Запускаем планировщик
    updater.run_scheduler()

if __name__ == '__main__':
    main() 