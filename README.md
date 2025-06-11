# Facebook Ad Spend Collector

Автоматизированная система для сбора данных о расходах на рекламу Facebook с использованием антидетект-браузеров. Система полностью контейнеризирована с помощью Docker и включает веб-интерфейс для управления.

## 🚀 Особенности

- **Полная автоматизация**: Автоматический сбор данных по расписанию без ручного вмешательства
- **Безопасность**: Использование антидетект-браузеров для имитации реальных пользователей
- **Веб-интерфейс**: Простой и интуитивный интерфейс для управления профилями и настройками
- **Docker**: Полная контейнеризация для легкого развертывания
- **Масштабируемость**: Поддержка множественных профилей и рекламных аккаунтов
- **Мониторинг**: Подробное логирование и статистика

## 📋 Требования

- Docker Desktop (Windows/Mac) или Docker Engine (Linux)
- Docker Compose
- Антидетект-браузер (Dolphin Anty, AdsPower, или Undetectable.io)
- Facebook Access Token с правами на чтение рекламных данных

## 🛠 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/ohchillman/testspendproj.git
cd testspendproj
```

### 2. Настройка переменных окружения

Скопируйте файл `.env` и отредактируйте его:

```bash
cp .env .env.local
nano .env.local
```

Основные настройки для изменения:

```env
# Facebook API (ОБЯЗАТЕЛЬНО ИЗМЕНИТЬ)
FACEBOOK_ACCESS_TOKEN=ваш_реальный_токен_facebook

# Антидетект-браузер (настройте под ваш браузер)
ANTI_DETECT_BROWSER_API_URL=http://host.docker.internal:3001/v1.0
ANTI_DETECT_BROWSER_TYPE=dolphin_anty

# База данных (можете оставить как есть)
POSTGRES_PASSWORD=ваш_безопасный_пароль
```

### 3. Запуск системы

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

### 4. Доступ к веб-интерфейсу

Откройте браузер и перейдите по адресу: http://localhost:5000

## 📖 Подробная инструкция по развертыванию

### Шаг 1: Подготовка окружения

#### Установка Docker

**Windows/Mac:**
1. Скачайте Docker Desktop с официального сайта
2. Установите и запустите Docker Desktop
3. Убедитесь, что Docker работает: `docker --version`

**Linux (Ubuntu/Debian):**
```bash
# Обновление пакетов
sudo apt update

# Установка Docker
sudo apt install docker.io docker-compose

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Перезагрузка для применения изменений
sudo reboot
```

#### Настройка антидетект-браузера

**Dolphin Anty:**
1. Установите Dolphin Anty с официального сайта
2. Запустите приложение
3. Убедитесь, что API включен (обычно порт 3001)
4. Создайте профили для ваших Facebook аккаунтов

**AdsPower:**
1. Установите AdsPower
2. Включите API (обычно порт 50325)
3. Создайте профили

**Undetectable.io:**
1. Установите Undetectable.io
2. Включите API (обычно порт 9222)
3. Создайте профили

### Шаг 2: Получение Facebook Access Token

1. Перейдите в Facebook Developers Console
2. Создайте новое приложение или используйте существующее
3. Получите токен с правами:
   - `ads_read`
   - `ads_management`
   - `business_management`

### Шаг 3: Конфигурация системы

#### Настройка .env файла

```env
# ===========================================
# НАСТРОЙКИ БАЗЫ ДАННЫХ
# ===========================================
POSTGRES_DB=facebook_spend_db
POSTGRES_USER=facebook_user
POSTGRES_PASSWORD=ИЗМЕНИТЕ_НА_БЕЗОПАСНЫЙ_ПАРОЛЬ
DATABASE_URL=postgresql://facebook_user:ИЗМЕНИТЕ_НА_БЕЗОПАСНЫЙ_ПАРОЛЬ@postgres:5432/facebook_spend_db
DATABASE_TYPE=postgresql

# ===========================================
# FACEBOOK API
# ===========================================
FACEBOOK_ACCESS_TOKEN=ВСТАВЬТЕ_ВАШ_РЕАЛЬНЫЙ_ТОКЕН
FACEBOOK_API_VERSION=v18.0

# ===========================================
# АНТИДЕТЕКТ-БРАУЗЕР
# ===========================================
# Для Dolphin Anty
ANTI_DETECT_BROWSER_API_URL=http://host.docker.internal:3001/v1.0
ANTI_DETECT_BROWSER_TYPE=dolphin_anty

# Для AdsPower (раскомментируйте если используете)
# ANTI_DETECT_BROWSER_API_URL=http://host.docker.internal:50325
# ANTI_DETECT_BROWSER_TYPE=adspower

# Для Undetectable.io (раскомментируйте если используете)
# ANTI_DETECT_BROWSER_API_URL=http://host.docker.internal:9222
# ANTI_DETECT_BROWSER_TYPE=undetectable

# ===========================================
# НАСТРОЙКИ СБОРА ДАННЫХ
# ===========================================
DAYS_BACK=1
DAILY_BREAKDOWN=true
DELAY_BETWEEN_PROFILES=10

# ===========================================
# ПЛАНИРОВЩИК
# ===========================================
SCHEDULER_INTERVAL_HOURS=6
SCHEDULER_ENABLED=true

# ===========================================
# БЕЗОПАСНОСТЬ
# ===========================================
FLASK_SECRET_KEY=ИЗМЕНИТЕ_НА_СЛУЧАЙНУЮ_СТРОКУ

# ===========================================
# ЛОГИРОВАНИЕ
# ===========================================
LOG_LEVEL=INFO
LOG_FILE=/app/logs/facebook_spend_collector.log
```

### Шаг 4: Запуск и тестирование

#### Запуск системы

```bash
# Переход в директорию проекта
cd testspendproj

# Создание необходимых директорий
mkdir -p logs data

# Запуск всех сервисов
docker-compose up -d

# Ожидание запуска (30-60 секунд)
sleep 60

# Проверка статуса всех контейнеров
docker-compose ps
```

#### Автоматическое тестирование

```bash
# Запуск скрипта тестирования
./docker-test.sh
```

#### Ручное тестирование

```bash
# Проверка веб-интерфейса
curl http://localhost:5000

# Проверка API
curl http://localhost:5000/api/profiles

# Проверка базы данных
docker-compose exec postgres psql -U facebook_user -d facebook_spend_db -c "SELECT * FROM profiles;"

# Просмотр логов
docker-compose logs facebook-spend-app
docker-compose logs scheduler
docker-compose logs postgres
```

## 🎛 Использование веб-интерфейса

### Главная страница (Дашборд)

- Просмотр общей статистики
- Количество профилей и их статус
- Общие расходы и метрики
- Кнопка ручного запуска сбора данных

### Управление профилями

1. Перейдите на страницу "Профили"
2. Нажмите "Добавить профиль"
3. Заполните форму:
   - **ID Профиля**: UUID профиля из антидетект-браузера
   - **ID Рекламного аккаунта**: ID аккаунта Facebook (без префикса "act_")
   - **Валюта**: Валюта аккаунта (USD, EUR, RUB, GBP)
   - **URL Прокси**: Оставьте пустым если прокси управляется браузером
   - **ID Объявлений**: Список конкретных объявлений или пустое для всех

### Настройки системы

1. Перейдите на страницу "Настройки"
2. Настройте параметры:
   - Facebook Access Token
   - URL API антидетект-браузера
   - Интервал сбора данных
   - Задержки между профилями

### Просмотр логов

- Страница "Логи" показывает все события системы
- Фильтрация по уровню логирования
- Поиск по тексту
- Автообновление каждые 30 секунд

## 🔧 Управление системой

### Основные команды Docker

```bash
# Запуск всех сервисов
docker-compose up -d

# Остановка всех сервисов
docker-compose down

# Перезапуск конкретного сервиса
docker-compose restart facebook-spend-app

# Просмотр логов
docker-compose logs -f facebook-spend-app

# Просмотр статуса
docker-compose ps

# Обновление образов
docker-compose pull
docker-compose up -d --force-recreate
```

### Резервное копирование данных

```bash
# Создание бэкапа базы данных
docker-compose exec postgres pg_dump -U facebook_user facebook_spend_db > backup.sql

# Восстановление из бэкапа
docker-compose exec -T postgres psql -U facebook_user facebook_spend_db < backup.sql

# Копирование логов
docker cp facebook-spend-app:/app/logs ./logs_backup
```

### Мониторинг

```bash
# Мониторинг ресурсов
docker stats

# Просмотр логов в реальном времени
docker-compose logs -f

# Проверка здоровья сервисов
curl http://localhost:5000/api/stats
```

## 🚨 Устранение неполадок

### Проблема: Контейнеры не запускаются

**Решение:**
```bash
# Проверка логов
docker-compose logs

# Пересборка образов
docker-compose build --no-cache
docker-compose up -d
```

### Проблема: Веб-интерфейс недоступен

**Решение:**
```bash
# Проверка статуса контейнера
docker-compose ps facebook-spend-app

# Проверка портов
netstat -tulpn | grep 5000

# Перезапуск сервиса
docker-compose restart facebook-spend-app
```

### Проблема: Не подключается к антидетект-браузеру

**Решение:**
1. Убедитесь, что антидетект-браузер запущен
2. Проверьте, что API включен в настройках браузера
3. Проверьте URL в настройках системы
4. Тестирование подключения:

```bash
# Из контейнера
docker-compose exec facebook-spend-app curl http://host.docker.internal:3001/v1.0/browser_profiles

# С хост-машины
curl http://localhost:3001/v1.0/browser_profiles
```

### Проблема: Ошибки Facebook API

**Решение:**
1. Проверьте валидность токена доступа
2. Убедитесь в наличии необходимых разрешений
3. Проверьте лимиты API
4. Просмотрите логи для деталей ошибки

### Проблема: База данных недоступна

**Решение:**
```bash
# Проверка статуса PostgreSQL
docker-compose ps postgres

# Подключение к базе данных
docker-compose exec postgres psql -U facebook_user facebook_spend_db

# Перезапуск базы данных
docker-compose restart postgres
```

## 📊 Структура данных

### Таблица profiles

| Поле | Тип | Описание |
|------|-----|----------|
| id | SERIAL | Уникальный идентификатор |
| profile_id | VARCHAR(255) | ID профиля антидетект-браузера |
| ad_account_id | VARCHAR(255) | ID рекламного аккаунта Facebook |
| currency | VARCHAR(10) | Валюта аккаунта |
| proxy_url | TEXT | URL прокси (опционально) |
| ad_ids | TEXT | Список ID объявлений через запятую |
| is_active | BOOLEAN | Активен ли профиль |
| created_at | TIMESTAMP | Дата создания |
| updated_at | TIMESTAMP | Дата обновления |

### Таблица ad_spend

| Поле | Тип | Описание |
|------|-----|----------|
| id | SERIAL | Уникальный идентификатор |
| profile_id | VARCHAR(255) | ID профиля |
| ad_account_id | VARCHAR(255) | ID рекламного аккаунта |
| ad_id | VARCHAR(255) | ID объявления |
| ad_name | TEXT | Название объявления |
| campaign_id | VARCHAR(255) | ID кампании |
| campaign_name | TEXT | Название кампании |
| adset_id | VARCHAR(255) | ID группы объявлений |
| adset_name | TEXT | Название группы объявлений |
| date_start | DATE | Дата начала периода |
| date_stop | DATE | Дата окончания периода |
| spend | DECIMAL(10,2) | Расходы |
| impressions | INTEGER | Показы |
| clicks | INTEGER | Клики |
| ctr | DECIMAL(5,4) | CTR (Click-through rate) |
| cpc | DECIMAL(10,2) | CPC (Cost per click) |
| cpm | DECIMAL(10,2) | CPM (Cost per mille) |
| currency | VARCHAR(10) | Валюта |
| created_at | TIMESTAMP | Дата создания записи |
| updated_at | TIMESTAMP | Дата обновления записи |

## 🔐 Безопасность

### Рекомендации по безопасности

1. **Токены доступа**: Никогда не публикуйте реальные токены в публичных репозиториях
2. **Пароли**: Используйте сложные пароли для базы данных
3. **Сеть**: Не выставляйте порты базы данных в интернет
4. **Обновления**: Регулярно обновляйте Docker образы
5. **Логи**: Не логируйте чувствительные данные

### Настройка firewall

```bash
# Разрешить только локальные подключения к портам
sudo ufw allow from 127.0.0.1 to any port 5000
sudo ufw allow from 127.0.0.1 to any port 5432
```

## 📈 Масштабирование

### Горизонтальное масштабирование

Для обработки большого количества профилей можно запустить несколько экземпляров планировщика:

```yaml
# В docker-compose.yml
scheduler-1:
  build: .
  command: python scheduler_service.py
  environment:
    - SCHEDULER_INSTANCE=1

scheduler-2:
  build: .
  command: python scheduler_service.py
  environment:
    - SCHEDULER_INSTANCE=2
```

### Оптимизация производительности

1. **База данных**: Используйте PostgreSQL для больших объемов данных
2. **Индексы**: Добавьте индексы для часто используемых запросов
3. **Кэширование**: Реализуйте кэширование для API запросов
4. **Пулы соединений**: Настройте пулы соединений к базе данных

## 🤝 Поддержка

### Получение помощи

1. Проверьте логи системы
2. Просмотрите раздел "Устранение неполадок"
3. Создайте issue в GitHub репозитории
4. Приложите логи и конфигурацию (без чувствительных данных)

### Сообщение об ошибках

При сообщении об ошибке включите:
- Версию Docker и Docker Compose
- Операционную систему
- Конфигурацию .env (без токенов)
- Логи ошибки
- Шаги для воспроизведения

## 📝 Лицензия

Этот проект распространяется под лицензией MIT. См. файл LICENSE для деталей.

## 🙏 Благодарности

- Facebook Graph API за предоставление данных
- Разработчикам антидетект-браузеров за API
- Сообществу Docker за отличную платформу контейнеризации
- Команде Flask за простой и мощный веб-фреймворк

