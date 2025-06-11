# orchestrator.py
"""
Главный оркестратор системы сбора данных Facebook Ad Spend
Координирует работу всех модулей
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from anti_detect_browser_manager import AntiDetectBrowserManager
from facebook_api_client import FacebookAPIClient
from database_manager import DatabaseManager
from config_manager import config_manager # Импортируем глобальный экземпляр ConfigManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('facebook_spend_collector.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class FacebookSpendOrchestrator:
    """Главный оркестратор системы"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Инициализация оркестратора
        
        Args:
            config_dict: Словарь с конфигурацией (опционально)
        """
        if config_dict:
            self.config = config_dict
        else:
            self.config = config_manager.get_all() # Используем config_manager для получения всей конфигурации
        
        # Инициализация компонентов
        self.browser_manager = AntiDetectBrowserManager(
            api_url=self.config.get('anti_detect_browser_api_url', 'http://localhost:3001/v1.0')
        )
        
        self.facebook_client = FacebookAPIClient(
            access_token=self.config['facebook_access_token'],
            api_version=self.config.get('facebook_api_version', 'v18.0')
        )
        
        self.db_manager = DatabaseManager(
            db_path=self.config.get('database_url', 'facebook_spend_data.db'), # Изменено на database_url
            db_type=self.config.get('database_type', 'sqlite')
        )
        
    # Удаляем метод load_config, так как конфигурация теперь загружается через ConfigManager
    # def load_config(self, config_path: str) -> Dict[str, Any]:
    #     """
    #     Загружает конфигурацию из JSON файла
    #     
    #     Args:
    #         config_path: Путь к файлу конфигурации
    #         
    #     Returns:
    #         Словарь с конфигурацией
    #     """
    #     try:
    #         with open(config_path, 'r', encoding='utf-8') as f:
    #             config = json.load(f)
    #             logger.info(f"Конфигурация загружена из {config_path}")
    #             return config
    #     except FileNotFoundError:
    #         logger.error(f"Файл конфигурации {config_path} не найден")
    #         raise
    #     except json.JSONDecodeError as e:
    #         logger.error(f"Ошибка при парсинге JSON конфигурации: {e}")
    #         raise
            
    def get_date_range(self) -> tuple:
        """
        Получает диапазон дат для сбора данных
        
        Returns:
            Кортеж (start_date, end_date) в формате YYYY-MM-DD
        """
        # По умолчанию собираем данные за вчерашний день
        yesterday = datetime.now() - timedelta(days=1)
        
        # Можно настроить в конфигурации
        days_back = self.config.get('days_back', 1)
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        end_date = yesterday.strftime('%Y-%m-%d')
        
        return start_date, end_date
        
    def process_profile(self, profile_config: Dict[str, Any], start_date: str, end_date: str) -> bool:
        """
        Обрабатывает один профиль: запускает браузер, собирает данные, сохраняет в БД
        
        Args:
            profile_config: Конфигурация профиля
            start_date: Начальная дата для сбора данных
            end_date: Конечная дата для сбора данных
            
        Returns:
            True если обработка прошла успешно
        """
        profile_id = profile_config['profile_id']
        ad_account_id = profile_config['ad_account_id']
        
        logger.info(f"Начинаем обработку профиля {profile_id} для аккаунта {ad_account_id}")
        
        try:
            # 1. Запускаем профиль антидетект-браузера
            browser_info = self.browser_manager.launch_profile(profile_id)
            logger.info(f"Профиль {profile_id} запущен")
            
            # Небольшая пауза для полной инициализации браузера
            time.sleep(5)
            
            # 2. Настраиваем прокси для запросов (если доступен)
            proxy_config = None
            if 'proxy_url' in profile_config:
                proxy_config = {
                    'http': profile_config['proxy_url'],
                    'https': profile_config['proxy_url']
                }
            elif 'ws' in browser_info and 'port' in browser_info:
                # Если антидетект-браузер предоставляет локальный прокси
                local_proxy = f"socks5://127.0.0.1:{browser_info['port']}"
                proxy_config = {
                    'http': local_proxy,
                    'https': local_proxy
                }
            
            # 3. Получаем список объявлений (если нужны конкретные ad_ids)
            ad_ids = profile_config.get('ad_ids')
            if not ad_ids:
                # Если ad_ids не указаны, получаем все объявления аккаунта
                ads = self.facebook_client.get_ads(ad_account_id, limit=1000)
                ad_ids = [ad['id'] for ad in ads]
                logger.info(f"Получено {len(ad_ids)} объявлений для аккаунта {ad_account_id}")
            
            # 4. Получаем данные о расходах
            if self.config.get('daily_breakdown', True):
                # Получаем ежедневную разбивку
                insights = self.facebook_client.get_daily_insights(
                    ad_account_id=ad_account_id,
                    start_date=start_date,
                    end_date=end_date,
                    ad_ids=ad_ids,
                    proxy_config=proxy_config
                )
            else:
                # Получаем общие данные за период
                insights = self.facebook_client.get_ad_insights(
                    ad_account_id=ad_account_id,
                    start_date=start_date,
                    end_date=end_date,
                    ad_ids=ad_ids,
                    proxy_config=proxy_config
                )
            
            logger.info(f"Получено {len(insights)} записей о расходах")
            
            # 5. Подготавливаем данные для сохранения в БД
            db_records = []
            for insight in insights:
                record = {
                    'profile_id': profile_id,
                    'ad_account_id': ad_account_id,
                    'ad_id': insight.get('ad_id', ''),
                    'ad_name': insight.get('ad_name', ''),
                    'date_start': insight.get('date_start', start_date),
                    'date_end': insight.get('date_stop', end_date),
                    'spend': insight.get('spend', 0),
                    'currency': profile_config.get('currency', 'USD'),
                    'impressions': insight.get('impressions', 0),
                    'clicks': insight.get('clicks', 0),
                    'ctr': insight.get('ctr', 0),
                    'cpc': insight.get('cpc', 0),
                    'cpm': insight.get('cpm', 0)
                }
                db_records.append(record)
            
            # 6. Сохраняем данные в базу данных
            saved_count = self.db_manager.insert_multiple_spend_data(db_records)
            logger.info(f"Сохранено {saved_count} записей для профиля {profile_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обработке профиля {profile_id}: {e}")
            return False
            
        finally:
            # 7. Закрываем профиль антидетект-браузера
            try:
                self.browser_manager.close_profile(profile_id)
                logger.info(f"Профиль {profile_id} закрыт")
            except Exception as e:
                logger.error(f"Ошибка при закрытии профиля {profile_id}: {e}")
                
    def run(self):
        """
        Главный метод запуска сбора данных
        """
        logger.info("Запуск системы сбора данных Facebook Ad Spend")
        
        try:
            # Тестируем подключение к Facebook API
            self.facebook_client.test_connection()
            
            # Получаем диапазон дат для сбора
            start_date, end_date = self.get_date_range()
            logger.info(f"Сбор данных за период: {start_date} - {end_date}")
            
            # Обрабатываем каждый профиль
            profiles = self.config.get('profiles', [])
            successful_profiles = 0
            
            for i, profile_config in enumerate(profiles, 1):
                logger.info(f"Обработка профиля {i}/{len(profiles)}")
                
                if self.process_profile(profile_config, start_date, end_date):
                    successful_profiles += 1
                
                # Пауза между профилями для снижения нагрузки
                delay = self.config.get('delay_between_profiles', 10)
                if i < len(profiles):  # Не делаем паузу после последнего профиля
                    logger.info(f"Пауза {delay} секунд перед следующим профилем")
                    time.sleep(delay)
            
            logger.info(f"Обработка завершена. Успешно обработано {successful_profiles}/{len(profiles)} профилей")
            
        except Exception as e:
            logger.error(f"Критическая ошибка в работе оркестратора: {e}")
            raise

def run_orchestrator():
    """Функция для запуска оркестратора (используется в main.py)"""
    orchestrator = FacebookSpendOrchestrator()
    orchestrator.run()

if __name__ == "__main__":
    run_orchestrator()


