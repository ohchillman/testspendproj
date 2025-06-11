#!/bin/bash

# install.sh - Скрипт установки системы сбора данных Facebook Ad Spend

echo "=== Установка системы сбора данных Facebook Ad Spend ==="

# Проверяем наличие Python 3
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python 3 не установлен"
    exit 1
fi

echo "Python 3 найден: $(python3 --version)"

# Создаем виртуальное окружение
echo "Создание виртуального окружения..."
python3 -m venv venv

# Активируем виртуальное окружение
echo "Активация виртуального окружения..."
source venv/bin/activate

# Обновляем pip
echo "Обновление pip..."
pip install --upgrade pip

# Устанавливаем зависимости
echo "Установка зависимостей..."
pip install -r requirements.txt

# Делаем main.py исполняемым
echo "Настройка прав доступа..."
chmod +x main.py

# Создаем директорию для логов
mkdir -p logs

echo "=== Установка завершена ==="
echo ""
echo "Следующие шаги:"
echo "1. Отредактируйте config.json и укажите ваши данные:"
echo "   - Facebook Access Token"
echo "   - ID профилей антидетект-браузера"
echo "   - ID рекламных аккаунтов"
echo "   - Настройки прокси"
echo ""
echo "2. Протестируйте систему:"
echo "   source venv/bin/activate"
echo "   python3 main.py"
echo ""
echo "3. Настройте cron job для автоматического запуска:"
echo "   crontab -e"
echo "   Добавьте строку:"
echo "   0 */6 * * * $(pwd)/venv/bin/python3 $(pwd)/main.py >> $(pwd)/logs/cron.log 2>&1"
echo ""
echo "4. Для работы с PostgreSQL (опционально):"
echo "   pip install psycopg2-binary"
echo "   Измените database_type в config.json на 'postgresql'"

