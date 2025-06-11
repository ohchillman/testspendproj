# anti_detect_browser_manager.py
"""
Модуль для управления профилями антидетект-браузера
Поддерживает Dolphin Anty API
"""

import requests
import json
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class AntiDetectBrowserManager:
    """Менеджер для работы с антидетект-браузером через API"""
    
    def __init__(self, api_url: str = "http://localhost:3001/v1.0"):
        """
        Инициализация менеджера
        
        Args:
            api_url: URL API антидетект-браузера (по умолчанию для Dolphin Anty)
        """
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        
    def launch_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Запускает профиль антидетект-браузера
        
        Args:
            profile_id: ID профиля для запуска
            
        Returns:
            Информация о запущенном профиле (включая порт для подключения)
            
        Raises:
            requests.RequestException: При ошибке запроса к API
        """
        url = f"{self.api_url}/browser_profiles/{profile_id}/start"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Профиль {profile_id} успешно запущен")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при запуске профиля {profile_id}: {e}")
            raise
            
    def close_profile(self, profile_id: str) -> bool:
        """
        Закрывает профиль антидетект-браузера
        
        Args:
            profile_id: ID профиля для закрытия
            
        Returns:
            True если профиль успешно закрыт
            
        Raises:
            requests.RequestException: При ошибке запроса к API
        """
        url = f"{self.api_url}/browser_profiles/{profile_id}/stop"
        
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            
            logger.info(f"Профиль {profile_id} успешно закрыт")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при закрытии профиля {profile_id}: {e}")
            raise
            
    def get_profile_info(self, profile_id: str) -> Dict[str, Any]:
        """
        Получает информацию о профиле
        
        Args:
            profile_id: ID профиля
            
        Returns:
            Информация о профиле
            
        Raises:
            requests.RequestException: При ошибке запроса к API
        """
        url = f"{self.api_url}/browser_profiles/{profile_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Получена информация о профиле {profile_id}")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при получении информации о профиле {profile_id}: {e}")
            raise
            
    def get_all_profiles(self) -> list:
        """
        Получает список всех профилей
        
        Returns:
            Список профилей
            
        Raises:
            requests.RequestException: При ошибке запроса к API
        """
        url = f"{self.api_url}/browser_profiles"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Получен список профилей: {len(data.get('data', []))} профилей")
            return data.get('data', [])
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при получении списка профилей: {e}")
            raise
            
    def create_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создает новый профиль
        
        Args:
            profile_data: Данные для создания профиля
            
        Returns:
            Информация о созданном профиле
            
        Raises:
            requests.RequestException: При ошибке запроса к API
        """
        url = f"{self.api_url}/browser_profiles"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = self.session.post(url, headers=headers, data=json.dumps(profile_data))
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Профиль успешно создан: {data.get('browserProfileId')}")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при создании профиля: {e}")
            raise
            
    def delete_profile(self, profile_id: str) -> bool:
        """
        Удаляет профиль
        
        Args:
            profile_id: ID профиля для удаления
            
        Returns:
            True если профиль успешно удален
            
        Raises:
            requests.RequestException: При ошибке запроса к API
        """
        url = f"{self.api_url}/browser_profiles/{profile_id}"
        
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            
            logger.info(f"Профиль {profile_id} успешно удален")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при удалении профиля {profile_id}: {e}")
            raise

