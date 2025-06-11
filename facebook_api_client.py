# facebook_api_client.py
"""
Модуль для взаимодействия с Facebook Graph API
Поддерживает получение данных о расходах на рекламу и ad.id
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class FacebookAPIClient:
    """Клиент для работы с Facebook Graph API"""
    
    def __init__(self, access_token: str, api_version: str = "v18.0"):
        """
        Инициализация клиента
        
        Args:
            access_token: Facebook Access Token с необходимыми разрешениями
            api_version: Версия Graph API
        """
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}"
        self.session = requests.Session()
        
    def get_ad_accounts(self, user_id: str = "me") -> List[Dict[str, Any]]:
        """
        Получает список рекламных аккаунтов пользователя
        
        Args:
            user_id: ID пользователя (по умолчанию "me")
            
        Returns:
            Список рекламных аккаунтов
            
        Raises:
            requests.RequestException: При ошибке запроса к API
        """
        url = f"{self.base_url}/{user_id}/adaccounts"
        params = {
            "fields": "id,name,account_status,currency",
            "access_token": self.access_token
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            accounts = data.get('data', [])
            logger.info(f"Получено {len(accounts)} рекламных аккаунтов")
            return accounts
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при получении рекламных аккаунтов: {e}")
            raise
            
    def get_ads(self, ad_account_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Получает список объявлений для указанного рекламного аккаунта
        
        Args:
            ad_account_id: ID рекламного аккаунта (без префикса "act_")
            limit: Максимальное количество объявлений для получения
            
        Returns:
            Список объявлений с их ID и названиями
            
        Raises:
            requests.RequestException: При ошибке запроса к API
        """
        url = f"{self.base_url}/act_{ad_account_id}/ads"
        params = {
            "fields": "id,name,status,created_time",
            "limit": limit,
            "access_token": self.access_token
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            ads = data.get('data', [])
            logger.info(f"Получено {len(ads)} объявлений для аккаунта {ad_account_id}")
            return ads
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при получении объявлений для аккаунта {ad_account_id}: {e}")
            raise
            
    def get_ad_insights(self, ad_account_id: str, start_date: str, end_date: str, 
                       ad_ids: Optional[List[str]] = None, 
                       proxy_config: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Получает данные о расходах на рекламу за указанный период
        
        Args:
            ad_account_id: ID рекламного аккаунта (без префикса "act_")
            start_date: Начальная дата в формате YYYY-MM-DD
            end_date: Конечная дата в формате YYYY-MM-DD
            ad_ids: Список ID объявлений (если None, получает данные по всем объявлениям)
            proxy_config: Конфигурация прокси {"http": "...", "https": "..."}
            
        Returns:
            Список данных о расходах
            
        Raises:
            requests.RequestException: При ошибке запроса к API
        """
        url = f"{self.base_url}/act_{ad_account_id}/insights"
        
        params = {
            "fields": "ad_id,ad_name,spend,impressions,clicks,ctr,cpc,cpm",
            "time_range": json.dumps({
                "since": start_date,
                "until": end_date
            }),
            "level": "ad",
            "access_token": self.access_token
        }
        
        # Если указаны конкретные ad_ids, добавляем их в фильтр
        if ad_ids:
            params["filtering"] = json.dumps([{
                "field": "ad.id",
                "operator": "IN",
                "value": ad_ids
            }])
        
        try:
            # Используем прокси, если он предоставлен
            proxies = proxy_config if proxy_config else None
            
            response = self.session.get(url, params=params, proxies=proxies)
            response.raise_for_status()
            
            data = response.json()
            insights = data.get('data', [])
            logger.info(f"Получено {len(insights)} записей о расходах для аккаунта {ad_account_id}")
            return insights
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при получении данных о расходах для аккаунта {ad_account_id}: {e}")
            raise
            
    def get_daily_insights(self, ad_account_id: str, start_date: str, end_date: str,
                          ad_ids: Optional[List[str]] = None,
                          proxy_config: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Получает ежедневные данные о расходах на рекламу
        
        Args:
            ad_account_id: ID рекламного аккаунта (без префикса "act_")
            start_date: Начальная дата в формате YYYY-MM-DD
            end_date: Конечная дата в формате YYYY-MM-DD
            ad_ids: Список ID объявлений (если None, получает данные по всем объявлениям)
            proxy_config: Конфигурация прокси {"http": "...", "https": "..."}
            
        Returns:
            Список ежедневных данных о расходах
            
        Raises:
            requests.RequestException: При ошибке запроса к API
        """
        url = f"{self.base_url}/act_{ad_account_id}/insights"
        
        params = {
            "fields": "ad_id,ad_name,spend,impressions,clicks,date_start,date_stop",
            "time_range": json.dumps({
                "since": start_date,
                "until": end_date
            }),
            "time_increment": "1",  # Ежедневная разбивка
            "level": "ad",
            "access_token": self.access_token
        }
        
        # Если указаны конкретные ad_ids, добавляем их в фильтр
        if ad_ids:
            params["filtering"] = json.dumps([{
                "field": "ad.id",
                "operator": "IN",
                "value": ad_ids
            }])
        
        try:
            # Используем прокси, если он предоставлен
            proxies = proxy_config if proxy_config else None
            
            response = self.session.get(url, params=params, proxies=proxies)
            response.raise_for_status()
            
            data = response.json()
            insights = data.get('data', [])
            logger.info(f"Получено {len(insights)} ежедневных записей для аккаунта {ad_account_id}")
            return insights
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при получении ежедневных данных для аккаунта {ad_account_id}: {e}")
            raise
            
    def test_connection(self) -> bool:
        """
        Тестирует подключение к Facebook API
        
        Returns:
            True если подключение успешно
            
        Raises:
            requests.RequestException: При ошибке запроса к API
        """
        url = f"{self.base_url}/me"
        params = {
            "fields": "id,name",
            "access_token": self.access_token
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Подключение к Facebook API успешно. Пользователь: {data.get('name')}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при тестировании подключения к Facebook API: {e}")
            raise

