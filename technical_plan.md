# Детальный технический план реализации

## Введение

Данный документ представляет собой детальный технический план реализации системы автоматического сбора данных о расходах на рекламу в Facebook. Он основывается на архитектуре, описанной в предыдущем документе, и детализирует шаги, необходимые для создания каждого компонента системы, а также определяет используемые технологии и инструменты.

## 1. Менеджер профилей антидетект-браузера

### 1.1. Выбор антидетект-браузера

Для реализации этой системы критически важен выбор антидетект-браузера, который предоставляет полноценный API для управления профилями. Среди популярных вариантов:

*   **Dolphin Anty**: Имеет хорошо документированный API и активное сообщество.
*   **AdsPower**: Также предлагает API для автоматизации.
*   **Undetectable.io**: Предоставляет API для управления профилями.

**Рекомендация**: Для начала можно выбрать Dolphin Anty или AdsPower, так как они имеют достаточно зрелые API и примеры использования. В дальнейшем, при необходимости, можно будет адаптировать систему под другие браузеры.

### 1.2. Функциональность

Модуль менеджера профилей будет предоставлять следующие функции:

*   `launch_profile(profile_id)`: Запускает указанный профиль антидетект-браузера. Возвращает информацию о запущенном браузере (например, порт для подключения Selenium/Playwright, если это применимо).
*   `close_profile(profile_id)`: Закрывает указанный профиль.
*   `get_profile_info(profile_id)`: Получает детальную информацию о профиле (прокси, куки, отпечатки).
*   `create_profile(profile_data)`: Создает новый профиль с заданными параметрами.
*   `delete_profile(profile_id)`: Удаляет профиль.

### 1.3. Взаимодействие с API антидетект-браузера

Взаимодействие будет осуществляться через HTTP-запросы к локальному API антидетект-браузера. Для этого в Python будет использоваться библиотека `requests`.

Пример взаимодействия (псевдокод):

```python
import requests
import json

BASE_URL = "http://localhost:port/api/v1/"

def launch_dolphin_anty_profile(profile_id):
    url = f"{BASE_URL}browser/start"
    headers = {'Content-Type': 'application/json'}
    payload = {"uuid": profile_id}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    return response.json()

def close_dolphin_anty_profile(profile_id):
    url = f"{BASE_URL}browser/stop"
    headers = {'Content-Type': 'application/json'}
    payload = {"uuid": profile_id}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    return response.json()
```

## 2. Модуль взаимодействия с Facebook Graph API

### 2.1. Получение Access Token

Для работы с Facebook Graph API потребуется Access Token. Для автоматизированного сбора данных рекомендуется использовать System User Access Token или Long-Lived User Access Token, который имеет необходимые разрешения для доступа к рекламным аккаунтам. Процесс получения Access Token выходит за рамки данного документа, но важно убедиться, что токен имеет разрешения `ads_read` и `ads_management`.

### 2.2. Запросы к Graph API

Для получения данных о расходах и ad.id будут использоваться конечные точки `/{ad-account-id}/insights` и `/{ad-account-id}/ads`.

*   **Получение расходов (ad spend)**: Запрос к `/insights` с параметрами `fields=spend` и `time_range` или `time_increment`.
*   **Получение ad.id**: Запрос к `/ads` с параметрами `fields=id,name`.

### 2.3. Использование прокси и куки

Ключевой момент – это использование прокси и куки, ассоциированных с профилем антидетект-браузера. Если антидетект-браузер предоставляет локальный прокси-сервер (например, SOCKS5) для каждого запущенного профиля, то запросы `requests` можно будет направлять через этот прокси. Куки будут автоматически управляться антидетект-браузером, когда он запускает свой внутренний браузер.

Пример запроса с использованием прокси (псевдокод):

```python
import requests

def get_ad_spend(ad_account_id, access_token, proxy_url, start_date, end_date):
    url = f"https://graph.facebook.com/v18.0/act_{ad_account_id}/insights"
    params = {
        "fields": "spend",
        "time_range": json.dumps({"since": start_date, "until": end_date}),
        "access_token": access_token
    }
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    response = requests.get(url, params=params, proxies=proxies)
    response.raise_for_status()
    return response.json()
```

**Важное замечание**: Отпечатки браузера (user-agent, canvas fingerprint, WebGL и т.д.) управляются самим антидетект-браузером на уровне его движка. При использовании API антидетект-браузера для запуска профиля, все эти параметры будут автоматически применяться к сессии браузера, через которую будут проходить запросы. Таким образом, Facebook будет видеть запросы, исходящие от браузера с соответствующими отпечатками.

## 3. Модуль хранения данных

### 3.1. Выбор базы данных

*   **PostgreSQL**: Рекомендуется для структурированных данных и сложных запросов. Подходит для хранения исторических данных.
*   **SQLite**: Простой вариант для небольших проектов, не требующий отдельного сервера базы данных. Может быть использован для быстрого прототипирования.

**Рекомендация**: Для начала можно использовать SQLite для простоты развертывания, а затем перейти на PostgreSQL при увеличении объема данных или требований к производительности.

### 3.2. Структура данных

Предлагаемая структура таблицы для хранения данных о расходах:

| Поле           | Тип данных | Описание                                        |
| :------------- | :--------- | :---------------------------------------------- |
| `id`           | `INTEGER`  | Первичный ключ, автоинкремент                   |
| `profile_id`   | `TEXT`     | ID профиля антидетект-браузера/Facebook аккаунта |
| `ad_account_id`| `TEXT`     | ID рекламного аккаунта Facebook                 |
| `ad_id`        | `TEXT`     | ID объявления Facebook                          |
| `date`         | `DATE`     | Дата, за которую собраны данные                 |
| `spend`        | `REAL`     | Сумма расходов за указанный период             |
| `currency`     | `TEXT`     | Валюта расходов                                 |
| `timestamp`    | `DATETIME` | Время сбора данных                              |

### 3.3. Взаимодействие с базой данных

Для взаимодействия с базой данных в Python будет использоваться библиотека `SQLAlchemy` (для ORM) или `psycopg2` (для PostgreSQL) / `sqlite3` (для SQLite).

Пример (псевдокод для SQLite):

```python
import sqlite3
from datetime import datetime

def create_table(db_path="spend_data.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ad_spend (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id TEXT NOT NULL,
            ad_account_id TEXT NOT NULL,
            ad_id TEXT NOT NULL,
            date DATE NOT NULL,
            spend REAL NOT NULL,
            currency TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def insert_spend_data(db_path, data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ad_spend (profile_id, ad_account_id, ad_id, date, spend, currency)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data['profile_id'], data['ad_account_id'], data['ad_id'], data['date'], data['spend'], data['currency']))
    conn.commit()
    conn.close()
```

## 4. Оркестратор

Оркестратор будет главным скриптом, который управляет всем процессом. Он будет читать конфигурацию, итерироваться по профилям, запускать антидетект-браузеры, вызывать Facebook API и сохранять данные.

### 4.1. Конфигурация

Конфигурация может храниться в JSON или YAML файле. Пример `config.json`:

```json
{
    "anti_detect_browser_api_url": "http://localhost:8000/api/v1/",
    "database_path": "spend_data.db",
    "facebook_access_token": "YOUR_FACEBOOK_ACCESS_TOKEN",
    "profiles": [
        {
            "profile_id": "profile_uuid_1",
            "ad_account_id": "1234567890",
            "proxy_url": "socks5://user:pass@proxy.example.com:1080" // Если антидетект-браузер не предоставляет локальный прокси
        },
        {
            "profile_id": "profile_uuid_2",
            "ad_account_id": "0987654321",
            "proxy_url": "socks5://user:pass@proxy2.example.com:1080"
        }
    ]
}
```

### 4.2. Логика работы

1.  Загрузка конфигурации.
2.  Инициализация базы данных (создание таблицы, если не существует).
3.  Для каждого профиля в конфигурации:
    а.  Запуск профиля антидетект-браузера через его API.
    б.  Получение локального прокси-адреса от антидетект-браузера (если он предоставляет).
    в.  Выполнение запросов к Facebook Graph API для получения данных о расходах и ad.id за нужный диапазон времени, используя полученный прокси и Access Token.
    г.  Сохранение полученных данных в базу данных.
    д.  Закрытие профиля антидетект-браузера.
4.  Обработка ошибок и логирование.

## 5. Планировщик (Cron)

Для автоматического запуска скрипта будет использоваться `cron`.

### 5.1. Создание исполняемого скрипта

Основной скрипт Оркестратора (например, `main.py`) должен быть исполняемым. Рекомендуется использовать виртуальное окружение для управления зависимостями.

```bash
#!/usr/bin/env python3

# Активация виртуального окружения (если используется)
# source /path/to/your/venv/bin/activate

import os
import sys

# Добавление пути к скрипту в PYTHONPATH, если необходимо
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator import run_orchestrator

if __name__ == "__main__":
    run_orchestrator()
```

### 5.2. Настройка Cron Job

Для добавления задачи в cron, выполните команду `crontab -e` и добавьте строку:

```
0 */6 * * * /usr/bin/python3 /path/to/your/script/main.py >> /var/log/facebook_spend_collector.log 2>&1
```

Эта строка будет запускать скрипт `main.py` каждые 6 часов. Путь к `python3` и `main.py` должен быть абсолютным. Вывод скрипта будет перенаправлен в лог-файл.

## 6. Обработка ошибок и логирование

*   **Логирование**: Использовать стандартный модуль `logging` в Python для записи информации о ходе выполнения, предупреждений и ошибок. Логи должны быть достаточно подробными для отладки.
*   **Обработка исключений**: Использовать блоки `try-except` для обработки возможных ошибок при взаимодействии с API антидетект-браузера, Facebook API и базой данных.
*   **Повторные попытки**: Реализовать механизм повторных попыток для временных ошибок (например, сетевые проблемы).

## 7. Безопасность

*   **Access Token**: Facebook Access Token не должен храниться непосредственно в коде. Рекомендуется использовать переменные окружения или защищенные хранилища конфигурации.
*   **Прокси-данные**: Учетные данные для прокси также не должны быть в коде или открытом виде в конфигурации.

## Заключение

Данный технический план предоставляет подробное руководство по реализации системы сбора данных о расходах на рекламу в Facebook с использованием антидетект-браузеров. Следуя этим шагам, можно создать надежное и эффективное решение. После утверждения этого плана, можно будет перейти к написанию кода и тестированию.

