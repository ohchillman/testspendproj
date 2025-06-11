#!/usr/bin/env python3
"""
Главный скрипт для запуска системы сбора данных Facebook Ad Spend
Используется для запуска через cron
"""

import os
import sys
import logging

# Добавляем текущую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Устанавливаем рабочую директорию
os.chdir(current_dir)

from orchestrator import run_orchestrator

def main():
    """Главная функция"""
    try:
        # Настройка логирования для cron
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(current_dir, 'facebook_spend_collector.log')),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info("=== Запуск системы сбора данных Facebook Ad Spend ===")
        
        # Запускаем оркестратор
        run_orchestrator()
        
        logger.info("=== Система сбора данных завершила работу ===")
        
    except Exception as e:
        logging.error(f"Критическая ошибка в main.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

