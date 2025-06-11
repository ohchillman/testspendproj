# scheduler_service.py
"""
Сервис планировщика для автоматического запуска сбора данных
"""

import time
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

from config_manager import config_manager
from database_manager import DatabaseManager
from orchestrator import FacebookSpendOrchestrator

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config_manager.get('log_level', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config_manager.get('log_file', '/app/logs/scheduler.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SchedulerService:
    """Сервис планировщика для автоматического сбора данных"""
    
    def __init__(self):
        """Инициализация планировщика"""
        self.db_manager = DatabaseManager(
            db_path=config_manager.get('database_url'),
            db_type=config_manager.get('database_type')
        )
        self.interval_hours = config_manager.get('scheduler_interval_hours', 6)
        self.enabled = config_manager.get('scheduler_enabled', True)
        self.last_run = None
        
        logger.info(f"Планировщик инициализирован. Интервал: {self.interval_hours} часов, Включен: {self.enabled}")
    
    def get_active_profiles(self) -> List[Dict[str, Any]]:
        """Получает активные профили из базы данных"""
        select_sql = "SELECT * FROM profiles WHERE is_active = ? ORDER BY created_at"
        if config_manager.get('database_type') != 'sqlite':
            select_sql = "SELECT * FROM profiles WHERE is_active = %s ORDER BY created_at"
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(select_sql, (True,))
                
                if config_manager.get('database_type') == 'sqlite':
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                else:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении активных профилей: {e}")
            return []
    
    def should_run(self) -> bool:
        """Проверяет, нужно ли запускать сбор данных"""
        if not self.enabled:
            return False
        
        if self.last_run is None:
            return True
        
        time_since_last_run = datetime.now() - self.last_run
        return time_since_last_run >= timedelta(hours=self.interval_hours)
    
    def run_collection(self) -> bool:
        """Запускает сбор данных"""
        try:
            logger.info("Начинаем автоматический сбор данных...")
            
            # Получаем активные профили
            profiles_list = self.get_active_profiles()
            if not profiles_list:
                logger.warning("Нет активных профилей для сбора данных")
                return False
            
            logger.info(f"Найдено {len(profiles_list)} активных профилей")
            
            # Преобразуем профили в формат для оркестратора
            config = config_manager.to_legacy_format()
            config['profiles'] = []
            
            for profile in profiles_list:
                profile_config = {
                    'profile_id': profile['profile_id'],
                    'ad_account_id': profile['ad_account_id'],
                    'currency': profile.get('currency', 'USD'),
                    'proxy_url': profile.get('proxy_url', ''),
                    'ad_ids': profile.get('ad_ids', '').split(',') if profile.get('ad_ids') else []
                }
                config['profiles'].append(profile_config)
            
            # Запускаем оркестратор
            orchestrator = FacebookSpendOrchestrator(config_dict=config)
            orchestrator.run()
            
            self.last_run = datetime.now()
            logger.info(f"Сбор данных завершен успешно в {self.last_run}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при автоматическом сборе данных: {e}")
            return False
    
    def run_forever(self):
        """Запускает планировщик в бесконечном цикле"""
        logger.info("Запуск планировщика в режиме демона...")
        
        while True:
            try:
                if self.should_run():
                    logger.info("Время для запуска сбора данных")
                    success = self.run_collection()
                    
                    if success:
                        logger.info("Сбор данных выполнен успешно")
                    else:
                        logger.error("Сбор данных завершился с ошибкой")
                else:
                    next_run = self.last_run + timedelta(hours=self.interval_hours) if self.last_run else datetime.now()
                    logger.debug(f"Следующий запуск запланирован на: {next_run}")
                
                # Обновляем конфигурацию (может измениться через веб-интерфейс)
                self.interval_hours = config_manager.get('scheduler_interval_hours', 6)
                self.enabled = config_manager.get('scheduler_enabled', True)
                
                # Спим 5 минут перед следующей проверкой
                time.sleep(300)  # 5 минут
                
            except KeyboardInterrupt:
                logger.info("Получен сигнал остановки планировщика")
                break
            except Exception as e:
                logger.error(f"Неожиданная ошибка в планировщике: {e}")
                time.sleep(60)  # Спим минуту при ошибке
        
        logger.info("Планировщик остановлен")

def main():
    """Главная функция для запуска планировщика"""
    # Создаем директории если они не существуют
    os.makedirs('/app/logs', exist_ok=True)
    os.makedirs('/app/data', exist_ok=True)
    
    # Создаем и запускаем планировщик
    scheduler = SchedulerService()
    scheduler.run_forever()

if __name__ == '__main__':
    main()

