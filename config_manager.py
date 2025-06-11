# config_manager.py
"""
Модуль для управления конфигурацией из переменных окружения
"""

import os
from typing import Dict, Any, List
import json

class ConfigManager:
    """Менеджер конфигурации для чтения настроек из переменных окружения"""
    
    def __init__(self):
        """
        Инициализация менеджера конфигурации
        """
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Загружает конфигурацию из переменных окружения
        
        Returns:
            Словарь с конфигурацией
        """
        return {
            # Настройки базы данных
            'database_url': os.getenv('DATABASE_URL', 'postgresql://spend_user:spend_password@facebook-spend-postgres:5432/spend_db'), # Изменено на PostgreSQL
            'database_type': os.getenv('DATABASE_TYPE', 'postgresql'), # Изменено на PostgreSQL
            
            # Facebook API
            'facebook_access_token': os.getenv('FACEBOOK_ACCESS_TOKEN', ''),
            'facebook_api_version': os.getenv('FACEBOOK_API_VERSION', 'v18.0'),
            
            # Антидетект-браузер
            'anti_detect_browser_api_url': os.getenv('ANTI_DETECT_BROWSER_API_URL', 'http://localhost:3001/v1.0'),
            'anti_detect_browser_type': os.getenv('ANTI_DETECT_BROWSER_TYPE', 'dolphin_anty'),
            
            # Настройки сбора данных
            'days_back': int(os.getenv('DAYS_BACK', '1')),
            'daily_breakdown': os.getenv('DAILY_BREAKDOWN', 'true').lower() == 'true',
            'delay_between_profiles': int(os.getenv('DELAY_BETWEEN_PROFILES', '10')),
            
            # Веб-интерфейс
            'flask_secret_key': os.getenv('FLASK_SECRET_KEY', 'dev-secret-key'),
            'flask_host': os.getenv('FLASK_HOST', '0.0.0.0'),
            'flask_port': int(os.getenv('FLASK_PORT', '5000')),
            
            # Планировщик
            'scheduler_interval_hours': int(os.getenv('SCHEDULER_INTERVAL_HOURS', '6')),
            'scheduler_enabled': os.getenv('SCHEDULER_ENABLED', 'true').lower() == 'true',
            
            # Логирование
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'log_file': os.getenv('LOG_FILE', '/app/logs/facebook_spend_collector.log'),
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Получает значение конфигурации по ключу
        
        Args:
            key: Ключ конфигурации
            default: Значение по умолчанию
            
        Returns:
            Значение конфигурации
        """
        return self.config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """
        Получает всю конфигурацию
        
        Returns:
            Словарь с полной конфигурацией
        """
        return self.config.copy()
    
    def update(self, updates: Dict[str, Any]):
        """
        Обновляет конфигурацию
        
        Args:
            updates: Словарь с обновлениями
        """
        self.config.update(updates)
    
    def to_legacy_format(self) -> Dict[str, Any]:
        """
        Преобразует конфигурацию в формат, совместимый со старым кодом
        
        Returns:
            Конфигурация в старом формате
        """
        return {
            'anti_detect_browser_api_url': self.get('anti_detect_browser_api_url'),
            'facebook_access_token': self.get('facebook_access_token'),
            'facebook_api_version': self.get('facebook_api_version'),
            'database_path': self.get('database_url'),
            'database_type': self.get('database_type'),
            'days_back': self.get('days_back'),
            'daily_breakdown': self.get('daily_breakdown'),
            'delay_between_profiles': self.get('delay_between_profiles'),
            'profiles': []  # Профили будут загружаться из базы данных
        }

# Глобальный экземпляр менеджера конфигурации
config_manager = ConfigManager()


