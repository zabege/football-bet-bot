import requests
import json
from datetime import datetime, timedelta
from config import FOOTBALL_API_KEY, FOOTBALL_API_BASE_URL, REAL_MADRID_ID, BARCELONA_ID

class FootballAPI:
    def __init__(self):
        self.api_key = FOOTBALL_API_KEY
        self.base_url = FOOTBALL_API_BASE_URL
        self.headers = {
            'X-Auth-Token': self.api_key
        } if self.api_key else {}
    
    def get_team_matches(self, team_id, days=30):
        """Получение матчей команды на ближайшие дни"""
        if not self.api_key:
            return self._get_demo_matches()
        
        try:
            # Получаем матчи команды
            url = f"{self.base_url}/teams/{team_id}/matches"
            params = {
                'dateFrom': datetime.now().strftime('%Y-%m-%d'),
                'dateTo': (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d'),
                'status': 'SCHEDULED'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('matches', [])
            
        except requests.RequestException as e:
            print(f"Ошибка API: {e}")
            return self._get_demo_matches()
    
    def get_real_barcelona_matches(self):
        """Получение матчей Real Madrid и Barcelona с августа 2025 по июль 2026"""
        print("⚡ Используем захардкоженные матчи для быстрой загрузки...")
        matches = self._get_demo_matches()
        print(f"✅ Загружено {len(matches)} матчей")
        return matches
    
    def get_next_matches(self, count=10):
        """Получение ближайших матчей (по дате)"""
        matches = self._get_demo_matches()
        # Сортируем по дате и берем первые count матчей
        sorted_matches = sorted(matches, key=lambda x: x['utcDate'])
        return sorted_matches[:count]
    
    def get_nearest_match(self):
        """Получение ближайшего матча"""
        matches = self._get_demo_matches()
        # Сортируем по дате и берем первый
        sorted_matches = sorted(matches, key=lambda x: x['utcDate'])
        return sorted_matches[0] if sorted_matches else None
    
    def get_upcoming_matches_for_betting(self, count=10):
        """Получение ближайших матчей для ставок"""
        matches = self._get_demo_matches()
        # Сортируем по дате и берем первые count матчей
        sorted_matches = sorted(matches, key=lambda x: x['utcDate'])
        return sorted_matches[:count]
    
    def _get_team_matches(self, team_id, date_from, date_to):
        """Получение матчей команды за период"""
        url = f"{self.base_url}/teams/{team_id}/matches"
        params = {
            'dateFrom': date_from,
            'dateTo': date_to,
            'status': 'SCHEDULED'
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get('matches', [])
    
    def get_match_result(self, match_id):
        """Получение результата матча"""
        if not self.api_key:
            return None
        
        try:
            url = f"{self.base_url}/matches/{match_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            match = data.get('match', {})
            
            if match.get('status') == 'FINISHED':
                return {
                    'home_score': match['score']['fullTime']['home'],
                    'away_score': match['score']['fullTime']['away']
                }
            
            return None
            
        except requests.RequestException as e:
            print(f"Ошибка получения результата матча: {e}")
            return None
    
    def _get_demo_matches(self):
        """Актуальные матчи Real Madrid и Barcelona (август 2025 - май 2026)"""
        real_matches = [
            {'id': 544216, 'homeTeam': {'name': 'RCD Mallorca'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2025-08-16T17:30:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544218, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'CA Osasuna'}, 'utcDate': '2025-08-19T19:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544226, 'homeTeam': {'name': 'Levante UD'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2025-08-23T19:30:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544224, 'homeTeam': {'name': 'Real Oviedo'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2025-08-24T19:30:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544240, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'RCD Mallorca'}, 'utcDate': '2025-08-30T19:30:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544238, 'homeTeam': {'name': 'Rayo Vallecano de Madrid'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2025-08-31T19:30:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544250, 'homeTeam': {'name': 'Real Sociedad de Fútbol'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2025-09-14T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544242, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'Valencia CF'}, 'utcDate': '2025-09-14T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544259, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'RCD Espanyol de Barcelona'}, 'utcDate': '2025-09-21T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544252, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'Getafe CF'}, 'utcDate': '2025-09-21T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544264, 'homeTeam': {'name': 'Levante UD'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2025-09-24T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544267, 'homeTeam': {'name': 'Real Oviedo'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2025-09-24T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544271, 'homeTeam': {'name': 'Club Atlético de Madrid'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2025-09-28T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544272, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'Real Sociedad de Fútbol'}, 'utcDate': '2025-09-28T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544284, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'Villarreal CF'}, 'utcDate': '2025-10-05T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544286, 'homeTeam': {'name': 'Sevilla FC'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2025-10-05T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544295, 'homeTeam': {'name': 'Getafe CF'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2025-10-19T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544293, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'Girona FC'}, 'utcDate': '2025-10-19T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544307, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2025-10-26T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544316, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'Valencia CF'}, 'utcDate': '2025-11-02T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544313, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'Elche CF'}, 'utcDate': '2025-11-02T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544325, 'homeTeam': {'name': 'Rayo Vallecano de Madrid'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2025-11-09T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544327, 'homeTeam': {'name': 'RC Celta de Vigo'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2025-11-09T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544333, 'homeTeam': {'name': 'Elche CF'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2025-11-23T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544337, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'Athletic Club'}, 'utcDate': '2025-11-23T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544343, 'homeTeam': {'name': 'Girona FC'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2025-11-30T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544347, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'Deportivo Alavés'}, 'utcDate': '2025-11-30T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544356, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'RC Celta de Vigo'}, 'utcDate': '2025-12-07T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544355, 'homeTeam': {'name': 'Real Betis Balompié'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2025-12-07T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544361, 'homeTeam': {'name': 'Deportivo Alavés'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2025-12-14T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544363, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'CA Osasuna'}, 'utcDate': '2025-12-14T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544375, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'Sevilla FC'}, 'utcDate': '2025-12-21T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544378, 'homeTeam': {'name': 'Villarreal CF'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2025-12-21T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544387, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'Real Betis Balompié'}, 'utcDate': '2026-01-04T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544386, 'homeTeam': {'name': 'RCD Espanyol de Barcelona'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2026-01-04T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544391, 'homeTeam': {'name': 'Athletic Club'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2026-01-11T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544395, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'Club Atlético de Madrid'}, 'utcDate': '2026-01-11T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544410, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'Levante UD'}, 'utcDate': '2026-01-18T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544409, 'homeTeam': {'name': 'Real Sociedad de Fútbol'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2026-01-18T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544420, 'homeTeam': {'name': 'Villarreal CF'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2026-01-25T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544413, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'Real Oviedo'}, 'utcDate': '2026-01-25T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544430, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'Rayo Vallecano de Madrid'}, 'utcDate': '2026-02-01T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544427, 'homeTeam': {'name': 'Elche CF'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2026-02-01T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544439, 'homeTeam': {'name': 'Valencia CF'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2026-02-08T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544434, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'RCD Mallorca'}, 'utcDate': '2026-02-08T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544444, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'Real Sociedad de Fútbol'}, 'utcDate': '2026-02-15T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544448, 'homeTeam': {'name': 'Girona FC'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2026-02-15T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544458, 'homeTeam': {'name': 'CA Osasuna'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2026-02-22T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544454, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'Levante UD'}, 'utcDate': '2026-02-22T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544469, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'Getafe CF'}, 'utcDate': '2026-03-01T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544461, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'Villarreal CF'}, 'utcDate': '2026-03-01T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544473, 'homeTeam': {'name': 'RC Celta de Vigo'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2026-03-08T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544471, 'homeTeam': {'name': 'Athletic Club'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2026-03-08T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544487, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'Elche CF'}, 'utcDate': '2026-03-15T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544483, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'Sevilla FC'}, 'utcDate': '2026-03-15T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544498, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'Club Atlético de Madrid'}, 'utcDate': '2026-03-22T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544492, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'Rayo Vallecano de Madrid'}, 'utcDate': '2026-03-22T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544505, 'homeTeam': {'name': 'RCD Mallorca'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2026-04-05T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544502, 'homeTeam': {'name': 'Club Atlético de Madrid'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2026-04-05T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544520, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'Girona FC'}, 'utcDate': '2026-04-12T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544512, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'RCD Espanyol de Barcelona'}, 'utcDate': '2026-04-12T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544522, 'homeTeam': {'name': 'Real Betis Balompié'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2026-04-19T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544527, 'homeTeam': {'name': 'Getafe CF'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2026-04-19T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544536, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'Deportivo Alavés'}, 'utcDate': '2026-04-22T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544532, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'RC Celta de Vigo'}, 'utcDate': '2026-04-22T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544544, 'homeTeam': {'name': 'RCD Espanyol de Barcelona'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2026-05-03T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544548, 'homeTeam': {'name': 'CA Osasuna'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2026-05-03T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544553, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2026-05-10T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544570, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'Real Oviedo'}, 'utcDate': '2026-05-13T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544561, 'homeTeam': {'name': 'Deportivo Alavés'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2026-05-13T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544580, 'homeTeam': {'name': 'Sevilla FC'}, 'awayTeam': {'name': 'Real Madrid CF'}, 'utcDate': '2026-05-17T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544573, 'homeTeam': {'name': 'FC Barcelona'}, 'awayTeam': {'name': 'Real Betis Balompié'}, 'utcDate': '2026-05-17T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544587, 'homeTeam': {'name': 'Real Madrid CF'}, 'awayTeam': {'name': 'Athletic Club'}, 'utcDate': '2026-05-24T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'},
            {'id': 544589, 'homeTeam': {'name': 'Valencia CF'}, 'awayTeam': {'name': 'FC Barcelona'}, 'utcDate': '2026-05-24T00:00:00Z', 'competition': {'name': 'Primera Division'}, 'status': 'SCHEDULED'}
        ]
        return real_matches
    
    def format_match_info(self, match):
        """Форматирование информации о матче для отображения"""
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        
        # Парсинг даты
        match_date = datetime.fromisoformat(match['utcDate'].replace('Z', '+00:00'))
        formatted_date = match_date.strftime('%d.%m.%Y %H:%M')
        
        tournament = match.get('competition', {}).get('name', 'Неизвестный турнир')
        
        return {
            'id': match['id'],
            'home_team': home_team,
            'away_team': away_team,
            'match_date': match_date,
            'formatted_date': formatted_date,
            'tournament': tournament,
            'status': match['status']
        } 