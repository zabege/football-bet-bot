import os
import json
from datetime import datetime
from typing import List, Tuple, Optional

class Database:
    def __init__(self):
        self.db_path = "bot_data.json"
        self.users = {}
        self.matches = {}
        self.bets = {}
        self.scores = {}
        self._load_data()
    
    def _load_data(self):
        """Загрузка данных из файла"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = data.get('users', {})
                    self.matches = data.get('matches', {})
                    self.bets = data.get('bets', {})
                    self.scores = data.get('scores', {})
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            # Если файл поврежден, начинаем с пустых данных
            self.users = {}
            self.matches = {}
            self.bets = {}
            self.scores = {}
    
    def _save_data(self):
        """Сохранение данных в файл"""
        try:
            data = {
                'users': self.users,
                'matches': self.matches,
                'bets': self.bets,
                'scores': self.scores
            }
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")
    
    def init_database(self):
        """Инициализация базы данных"""
        # База данных уже инициализирована в конструкторе
        pass
    
    def add_user(self, user_id: int, first_name: str, username: str = ""):
        """Добавление пользователя"""
        self.users[str(user_id)] = {
            'first_name': first_name,
            'username': username,
            'created_at': datetime.now().isoformat()
        }
        self._save_data()
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """Получение пользователя"""
        return self.users.get(str(user_id))
    
    def add_match(self, match_id: int, home_team: str, away_team: str, match_date: str, competition: str):
        """Добавление матча"""
        self.matches[str(match_id)] = {
            'home_team': home_team,
            'away_team': away_team,
            'match_date': match_date,
            'competition': competition,
            'home_score': None,
            'away_score': None,
            'status': 'scheduled'
        }
        self._save_data()
    
    def get_match(self, match_id: int) -> Optional[dict]:
        """Получение матча"""
        return self.matches.get(str(match_id))
    
    def update_match_score(self, match_id: int, home_score: int, away_score: int):
        """Обновление счета матча"""
        if str(match_id) in self.matches:
            self.matches[str(match_id)]['home_score'] = home_score
            self.matches[str(match_id)]['away_score'] = away_score
            self.matches[str(match_id)]['status'] = 'finished'
            self._save_data()
    
    def add_bet(self, user_id: int, match_id: int, predicted_winner: str, home_score: int, away_score: int) -> int:
        """Добавление ставки"""
        bet_id = len(self.bets) + 1
        self.bets[str(bet_id)] = {
            'user_id': user_id,
            'match_id': match_id,
            'predicted_winner': predicted_winner,
            'home_score': home_score,
            'away_score': away_score,
            'points': 0,
            'created_at': datetime.now().isoformat()
        }
        self._save_data()
        return bet_id
    
    def get_user_bets(self, user_id: int) -> List[dict]:
        """Получение ставок пользователя"""
        return [bet for bet in self.bets.values() if bet['user_id'] == user_id]
    
    def get_match_bets(self, match_id: int) -> List[dict]:
        """Получение ставок на матч"""
        return [bet for bet in self.bets.values() if bet['match_id'] == match_id]
    
    def update_bet_points(self, bet_id: int, points: int):
        """Обновление баллов ставки"""
        if str(bet_id) in self.bets:
            self.bets[str(bet_id)]['points'] = points
            self._save_data()
    
    def get_standings(self) -> List[Tuple]:
        """Получение таблицы результатов"""
        user_stats = {}
        
        # Подсчитываем статистику для каждого пользователя
        for bet in self.bets.values():
            user_id = bet['user_id']
            if user_id not in user_stats:
                user_stats[user_id] = {
                    'total_points': 0,
                    'correct_winners': 0,
                    'correct_scores': 0,
                    'total_bets': 0
                }
            
            user_stats[user_id]['total_points'] += bet['points']
            user_stats[user_id]['total_bets'] += 1
            
            # Подсчитываем правильные прогнозы
            if bet['points'] >= 1:  # Правильный победитель
                user_stats[user_id]['correct_winners'] += 1
            if bet['points'] >= 3:  # Правильный счет
                user_stats[user_id]['correct_scores'] += 1
        
        # Формируем результат
        standings = []
        for user_id, stats in user_stats.items():
            user = self.get_user(user_id)
            username = user['username'] if user else f"User{user_id}"
            
            standings.append((
                user_id,
                username,
                stats['total_points'],
                stats['correct_winners'],
                stats['correct_scores'],
                stats['total_bets']
            ))
        
        # Сортируем по баллам (по убыванию)
        standings.sort(key=lambda x: x[2], reverse=True)
        
        return standings
    
    def calculate_points_for_match(self, match_id: int):
        """Расчет баллов для всех ставок на матч"""
        match = self.get_match(match_id)
        if not match or match['status'] != 'finished':
            return
        
        home_score = match['home_score']
        away_score = match['away_score']
        
        # Определяем победителя
        if home_score > away_score:
            actual_winner = 'home'
        elif away_score > home_score:
            actual_winner = 'away'
        else:
            actual_winner = 'draw'
        
        # Обновляем баллы для всех ставок на этот матч
        for bet in self.get_match_bets(match_id):
            points = 0
            
            # Проверяем правильность победителя
            if bet['predicted_winner'] == actual_winner:
                points += 1
            
            # Проверяем правильность счета
            if bet['home_score'] == home_score and bet['away_score'] == away_score:
                points += 3
            
            # Обновляем баллы ставки
            self.update_bet_points(bet['user_id'], points) 