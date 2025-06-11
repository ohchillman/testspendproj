#!/bin/bash

# docker-test.sh - Скрипт для тестирования Docker-контейнеров

set -e

echo "🚀 Начинаем тестирование Docker-контейнеров..."

# Проверяем, что Docker и Docker Compose установлены
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен"
    exit 1
fi

echo "✅ Docker и Docker Compose найдены"

# Создаем необходимые директории
echo "📁 Создаем директории..."
mkdir -p logs data

# Останавливаем существующие контейнеры
echo "🛑 Останавливаем существующие контейнеры..."
docker-compose down --remove-orphans || true

# Собираем образы
echo "🔨 Собираем Docker образы..."
docker-compose build

# Запускаем контейнеры
echo "🚀 Запускаем контейнеры..."
docker-compose up -d

# Ждем запуска сервисов
echo "⏳ Ждем запуска сервисов..."
sleep 30

# Проверяем статус контейнеров
echo "📊 Проверяем статус контейнеров..."
docker-compose ps

# Проверяем логи
echo "📋 Проверяем логи..."
echo "--- Логи веб-приложения ---"
docker-compose logs facebook-spend-app | tail -10

echo "--- Логи базы данных ---"
docker-compose logs postgres | tail -10

echo "--- Логи планировщика ---"
docker-compose logs scheduler | tail -10

# Тестируем подключение к веб-интерфейсу
echo "🌐 Тестируем веб-интерфейс..."
if curl -f http://localhost:5000 > /dev/null 2>&1; then
    echo "✅ Веб-интерфейс доступен на http://localhost:5000"
else
    echo "❌ Веб-интерфейс недоступен"
fi

# Тестируем API
echo "🔌 Тестируем API..."
if curl -f http://localhost:5000/api/profiles > /dev/null 2>&1; then
    echo "✅ API доступен"
else
    echo "❌ API недоступен"
fi

# Тестируем подключение к базе данных
echo "🗄️ Тестируем подключение к базе данных..."
if docker-compose exec -T postgres psql -U facebook_user -d facebook_spend_db -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ База данных доступна"
else
    echo "❌ База данных недоступна"
fi

echo ""
echo "🎉 Тестирование завершено!"
echo ""
echo "📋 Полезные команды:"
echo "  Просмотр логов:     docker-compose logs -f"
echo "  Остановка:          docker-compose down"
echo "  Перезапуск:         docker-compose restart"
echo "  Веб-интерфейс:      http://localhost:5000"
echo "  База данных:        localhost:5432"
echo ""

