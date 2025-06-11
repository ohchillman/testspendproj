# docker_integration_guide.md
# Интеграция антидетект-браузера с Docker

## Проблема
Антидетект-браузеры (Dolphin Anty, AdsPower, Undetectable.io) обычно работают как десктопные приложения на хост-машине, в то время как наше приложение для сбора данных работает в Docker-контейнере. Необходимо обеспечить взаимодействие между контейнером и антидетект-браузером.

## Решение
Используем сетевое взаимодействие через API антидетект-браузера. Большинство современных антидетект-браузеров предоставляют HTTP API для управления профилями.

### Архитектура
```
Хост-машина:
├── Антидетект-браузер (Dolphin Anty) - порт 3001
├── Docker Desktop
└── Docker-контейнеры:
    ├── facebook-spend-app (веб-интерфейс) - порт 5000
    ├── scheduler (планировщик)
    └── postgres (база данных) - порт 5432
```

### Сетевое взаимодействие
- Контейнеры обращаются к хост-машине через `host.docker.internal`
- URL API антидетект-браузера: `http://host.docker.internal:3001/v1.0`
- Веб-интерфейс доступен на `http://localhost:5000`

## Настройка для разных антидетект-браузеров

### Dolphin Anty
- API URL: `http://host.docker.internal:3001/v1.0`
- Документация: https://docs.dolphin-anty.com/
- Порт по умолчанию: 3001

### AdsPower
- API URL: `http://host.docker.internal:50325`
- Документация: https://help.adspower.net/
- Порт по умолчанию: 50325

### Undetectable.io
- API URL: `http://host.docker.internal:9222`
- Документация: https://undetectable.io/
- Порт по умолчанию: 9222

## Конфигурация Docker

### docker-compose.yml
Используем `host.docker.internal` для доступа к хост-машине:

```yaml
services:
  facebook-spend-app:
    environment:
      - ANTI_DETECT_BROWSER_API_URL=http://host.docker.internal:3001/v1.0
```

### Переменные окружения
В `.env` файле:
```
ANTI_DETECT_BROWSER_API_URL=http://host.docker.internal:3001/v1.0
ANTI_DETECT_BROWSER_TYPE=dolphin_anty
```

## Безопасность
- API антидетект-браузера должен быть доступен только локально
- Используйте firewall для ограничения доступа к портам
- Не выставляйте API антидетект-браузера в интернет

## Тестирование подключения
Из контейнера можно протестировать подключение:
```bash
curl http://host.docker.internal:3001/v1.0/browser_profiles
```

