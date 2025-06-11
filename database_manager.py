# database_manager.py
"""
Модуль для управления базой данных
Поддерживает SQLite и PostgreSQL
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Менеджер для работы с базой данных"""
    
    def __init__(self, db_path: str = "facebook_spend_data.db", db_type: str = "sqlite"):
        """
        Инициализация менеджера базы данных
        
        Args:
            db_path: Путь к файлу базы данных (для SQLite) или строка подключения (для PostgreSQL)
            db_type: Тип базы данных ("sqlite" или "postgresql")
        """
        self.db_path = db_path
        self.db_type = db_type
        
        if db_type == "postgresql":
            try:
                import psycopg2
                self.psycopg2 = psycopg2
            except ImportError:
                raise ImportError("Для работы с PostgreSQL необходимо установить psycopg2: pip install psycopg2-binary")
        
        self.create_tables()
        
    @contextmanager
    def get_connection(self):
        """
        Контекстный менеджер для получения соединения с базой данных
        
        Yields:
            Соединение с базой данных
        """
        if self.db_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
        elif self.db_type == "postgresql":
            conn = self.psycopg2.connect(self.db_path)
        else:
            raise ValueError(f"Неподдерживаемый тип базы данных: {self.db_type}")
            
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
            
    def create_tables(self):
        """Создает необходимые таблицы в базе данных"""
        
        if self.db_type == "sqlite":
            create_sql = """
            CREATE TABLE IF NOT EXISTS ad_spend (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT NOT NULL,
                ad_account_id TEXT NOT NULL,
                ad_id TEXT NOT NULL,
                ad_name TEXT,
                date_start DATE NOT NULL,
                date_end DATE NOT NULL,
                spend REAL NOT NULL DEFAULT 0,
                currency TEXT DEFAULT 'USD',
                impressions INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                ctr REAL DEFAULT 0,
                cpc REAL DEFAULT 0,
                cpm REAL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(profile_id, ad_account_id, ad_id, date_start, date_end)
            )
            """
        elif self.db_type == "postgresql":
            create_sql = """
            CREATE TABLE IF NOT EXISTS ad_spend (
                id SERIAL PRIMARY KEY,
                profile_id VARCHAR(255) NOT NULL,
                ad_account_id VARCHAR(255) NOT NULL,
                ad_id VARCHAR(255) NOT NULL,
                ad_name TEXT,
                date_start DATE NOT NULL,
                date_end DATE NOT NULL,
                spend DECIMAL(10,2) NOT NULL DEFAULT 0,
                currency VARCHAR(10) DEFAULT 'USD',
                impressions INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                ctr DECIMAL(5,4) DEFAULT 0,
                cpc DECIMAL(10,2) DEFAULT 0,
                cpm DECIMAL(10,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(profile_id, ad_account_id, ad_id, date_start, date_end)
            )
            """
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(create_sql)
            logger.info("Таблицы базы данных созданы или уже существуют")
            
    def insert_spend_data(self, data: Dict[str, Any]) -> bool:
        """
        Вставляет данные о расходах в базу данных
        
        Args:
            data: Словарь с данными о расходах
            
        Returns:
            True если данные успешно вставлены
        """
        insert_sql = """
        INSERT OR REPLACE INTO ad_spend 
        (profile_id, ad_account_id, ad_id, ad_name, date_start, date_end, 
         spend, currency, impressions, clicks, ctr, cpc, cpm, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """ if self.db_type == "sqlite" else """
        INSERT INTO ad_spend 
        (profile_id, ad_account_id, ad_id, ad_name, date_start, date_end, 
         spend, currency, impressions, clicks, ctr, cpc, cpm, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (profile_id, ad_account_id, ad_id, date_start, date_end)
        DO UPDATE SET
            ad_name = EXCLUDED.ad_name,
            spend = EXCLUDED.spend,
            currency = EXCLUDED.currency,
            impressions = EXCLUDED.impressions,
            clicks = EXCLUDED.clicks,
            ctr = EXCLUDED.ctr,
            cpc = EXCLUDED.cpc,
            cpm = EXCLUDED.cpm,
            updated_at = EXCLUDED.updated_at
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(insert_sql, (
                    data['profile_id'],
                    data['ad_account_id'],
                    data['ad_id'],
                    data.get('ad_name', ''),
                    data['date_start'],
                    data['date_end'],
                    float(data.get('spend', 0)),
                    data.get('currency', 'USD'),
                    int(data.get('impressions', 0)),
                    int(data.get('clicks', 0)),
                    float(data.get('ctr', 0)),
                    float(data.get('cpc', 0)),
                    float(data.get('cpm', 0)),
                    datetime.now()
                ))
                logger.debug(f"Данные для ad_id {data['ad_id']} успешно сохранены")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных для ad_id {data.get('ad_id')}: {e}")
            return False
            
    def insert_multiple_spend_data(self, data_list: List[Dict[str, Any]]) -> int:
        """
        Вставляет множественные данные о расходах в базу данных
        
        Args:
            data_list: Список словарей с данными о расходах
            
        Returns:
            Количество успешно вставленных записей
        """
        success_count = 0
        
        for data in data_list:
            if self.insert_spend_data(data):
                success_count += 1
                
        logger.info(f"Успешно сохранено {success_count} из {len(data_list)} записей")
        return success_count
        
    def get_spend_data(self, profile_id: Optional[str] = None, 
                      ad_account_id: Optional[str] = None,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получает данные о расходах из базы данных с фильтрацией
        
        Args:
            profile_id: ID профиля для фильтрации
            ad_account_id: ID рекламного аккаунта для фильтрации
            start_date: Начальная дата для фильтрации (YYYY-MM-DD)
            end_date: Конечная дата для фильтрации (YYYY-MM-DD)
            
        Returns:
            Список записей о расходах
        """
        where_conditions = []
        params = []
        
        if profile_id:
            where_conditions.append("profile_id = ?")
            params.append(profile_id)
            
        if ad_account_id:
            where_conditions.append("ad_account_id = ?")
            params.append(ad_account_id)
            
        if start_date:
            where_conditions.append("date_start >= ?")
            params.append(start_date)
            
        if end_date:
            where_conditions.append("date_end <= ?")
            params.append(end_date)
            
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        select_sql = f"""
        SELECT * FROM ad_spend
        {where_clause}
        ORDER BY date_start DESC, ad_account_id, ad_id
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(select_sql, params)
                
                if self.db_type == "sqlite":
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                else:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
                    
        except Exception as e:
            logger.error(f"Ошибка при получении данных из базы: {e}")
            return []
            
    def get_total_spend_by_profile(self, start_date: Optional[str] = None,
                                  end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получает общие расходы по профилям
        
        Args:
            start_date: Начальная дата для фильтрации (YYYY-MM-DD)
            end_date: Конечная дата для фильтрации (YYYY-MM-DD)
            
        Returns:
            Список с общими расходами по профилям
        """
        where_conditions = []
        params = []
        
        if start_date:
            where_conditions.append("date_start >= ?")
            params.append(start_date)
            
        if end_date:
            where_conditions.append("date_end <= ?")
            params.append(end_date)
            
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        select_sql = f"""
        SELECT 
            profile_id,
            ad_account_id,
            COUNT(DISTINCT ad_id) as total_ads,
            SUM(spend) as total_spend,
            SUM(impressions) as total_impressions,
            SUM(clicks) as total_clicks,
            currency
        FROM ad_spend
        {where_clause}
        GROUP BY profile_id, ad_account_id, currency
        ORDER BY total_spend DESC
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(select_sql, params)
                
                if self.db_type == "sqlite":
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                else:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
                    
        except Exception as e:
            logger.error(f"Ошибка при получении общих данных по профилям: {e}")
            return []

