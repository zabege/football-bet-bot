#!/usr/bin/env python3
"""
Скрипт для миграции данных из bot_data.json в Railway Variables
"""

import json
import os
import subprocess
import sys

def migrate_data_to_railway():
    """Миграция данных из файла в Railway Variables"""
    
    # Проверяем, что мы в Railway
    if not os.getenv('RAILWAY_ENVIRONMENT'):
        print("❌ Этот скрипт должен запускаться в Railway")
        return False
    
    # Проверяем наличие файла данных
    if not os.path.exists('bot_data.json'):
        print("❌ Файл bot_data.json не найден")
        return False
    
    try:
        # Загружаем данные из файла
        with open('bot_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Конвертируем в JSON строку
        json_str = json.dumps(data, ensure_ascii=False)
        
        # Сохраняем в Railway Variables
        result = subprocess.run([
            'railway', 'variables', 'set', 
            'BOT_DATA_JSON=' + json_str
        ], check=True, capture_output=True, text=True)
        
        print("✅ Данные успешно мигрированы в Railway Variables!")
        print(f"📊 Пользователей: {len(data.get('users', {}))}")
        print(f"⚽ Матчей: {len(data.get('matches', {}))}")
        print(f"💰 Ставок: {len(data.get('bets', {}))}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при сохранении в Railway Variables: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Ошибка при миграции: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Начинаем миграцию данных в Railway Variables...")
    success = migrate_data_to_railway()
    if success:
        print("🎉 Миграция завершена успешно!")
    else:
        print("💥 Миграция не удалась!")
        sys.exit(1) 