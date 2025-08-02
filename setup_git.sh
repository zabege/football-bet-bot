#!/bin/bash

echo "🚀 Настройка Git репозитория для Railway деплоя..."

# Инициализация Git
git init

# Добавление файлов
git add .

# Первый коммит
git commit -m "Initial commit: Football Bet Bot for Railway"

# Переименование ветки в main
git branch -M main

echo "✅ Git репозиторий настроен!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Создайте репозиторий на GitHub"
echo "2. Выполните команды:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
echo "   git push -u origin main"
echo "3. Зайдите на railway.app и создайте новый проект"
echo "4. Выберите ваш GitHub репозиторий"
echo "5. Настройте переменные окружения в Railway Dashboard" 