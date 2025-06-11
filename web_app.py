# web_app.py
"""
Flask веб-приложение для управления системой сбора данных Facebook Ad Spend
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import logging
import os
from datetime import datetime
from typing import Dict, List, Any

from config_manager import config_manager
from database_manager import DatabaseManager
from orchestrator import FacebookSpendOrchestrator

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config_manager.get('log_level', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Создание Flask приложения
app = Flask(__name__)
app.secret_key = config_manager.get('flask_secret_key')

# Включение CORS для всех доменов
CORS(app)

# Инициализация менеджера базы данных
db_manager = DatabaseManager(
    db_path=config_manager.get('database_url'),
    db_type=config_manager.get('database_type')
)

class ProfileManager:
    """Менеджер для работы с профилями в базе данных"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._create_profiles_table()
    
    def _create_profiles_table(self):
        """Создает таблицу профилей если она не существует"""
        if self.db_manager.db_type == "sqlite":
            create_sql = """
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT UNIQUE NOT NULL,
                ad_account_id TEXT NOT NULL,
                currency TEXT DEFAULT 'USD',
                proxy_url TEXT,
                ad_ids TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        else:  # PostgreSQL
            create_sql = """
            CREATE TABLE IF NOT EXISTS profiles (
                id SERIAL PRIMARY KEY,
                profile_id VARCHAR(255) UNIQUE NOT NULL,
                ad_account_id VARCHAR(255) NOT NULL,
                currency VARCHAR(10) DEFAULT 'USD',
                proxy_url TEXT,
                ad_ids TEXT,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(create_sql)
    
    def get_all_profiles(self) -> List[Dict[str, Any]]:
        """Получает все профили"""
        select_sql = "SELECT * FROM profiles ORDER BY created_at DESC"
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(select_sql)
                
                if self.db_manager.db_type == "sqlite":
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                else:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении профилей: {e}")
            return []
    
    def add_profile(self, profile_data: Dict[str, Any]) -> bool:
        """Добавляет новый профиль"""
        insert_sql = """
        INSERT INTO profiles (profile_id, ad_account_id, currency, proxy_url, ad_ids, is_active, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """ if self.db_manager.db_type == "sqlite" else """
        INSERT INTO profiles (profile_id, ad_account_id, currency, proxy_url, ad_ids, is_active, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(insert_sql, (
                    profile_data['profile_id'],
                    profile_data['ad_account_id'],
                    profile_data.get('currency', 'USD'),
                    profile_data.get('proxy_url', ''),
                    profile_data.get('ad_ids', ''),
                    profile_data.get('is_active', True),
                    datetime.now()
                ))
                return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении профиля: {e}")
            return False
    
    def update_profile(self, profile_id: str, profile_data: Dict[str, Any]) -> bool:
        """Обновляет существующий профиль"""
        update_sql = """
        UPDATE profiles 
        SET ad_account_id = ?, currency = ?, proxy_url = ?, ad_ids = ?, is_active = ?, updated_at = ?
        WHERE profile_id = ?
        """ if self.db_manager.db_type == "sqlite" else """
        UPDATE profiles 
        SET ad_account_id = %s, currency = %s, proxy_url = %s, ad_ids = %s, is_active = %s, updated_at = %s
        WHERE profile_id = %s
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(update_sql, (
                    profile_data['ad_account_id'],
                    profile_data.get('currency', 'USD'),
                    profile_data.get('proxy_url', ''),
                    profile_data.get('ad_ids', ''),
                    profile_data.get('is_active', True),
                    datetime.now(),
                    profile_id
                ))
                return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении профиля: {e}")
            return False
    
    def delete_profile(self, profile_id: str) -> bool:
        """Удаляет профиль"""
        delete_sql = "DELETE FROM profiles WHERE profile_id = ?"
        if self.db_manager.db_type != "sqlite":
            delete_sql = "DELETE FROM profiles WHERE profile_id = %s"
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(delete_sql, (profile_id,))
                return True
        except Exception as e:
            logger.error(f"Ошибка при удалении профиля: {e}")
            return False

# Инициализация менеджера профилей
profile_manager = ProfileManager(db_manager)

@app.route('/')
def index():
    """Главная страница"""
    profiles = profile_manager.get_all_profiles()
    config = config_manager.get_all()
    
    # Получаем статистику
    total_spend_data = db_manager.get_total_spend_by_profile()
    
    return render_template('index.html', 
                         profiles=profiles, 
                         config=config,
                         total_spend_data=total_spend_data)

@app.route('/profiles')
def profiles():
    """Страница управления профилями"""
    profiles_list = profile_manager.get_all_profiles()
    return render_template('profiles.html', profiles=profiles_list)

@app.route('/settings')
def settings():
    """Страница настроек"""
    config = config_manager.get_all()
    return render_template('settings.html', config=config)

@app.route('/logs')
def logs():
    """Страница просмотра логов"""
    try:
        log_file = config_manager.get('log_file')
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
        else:
            log_content = "Лог-файл не найден"
    except Exception as e:
        log_content = f"Ошибка при чтении лог-файла: {e}"
    
    return render_template('logs.html', log_content=log_content)

# API эндпоинты
@app.route('/api/profiles', methods=['GET'])
def api_get_profiles():
    """API: Получить все профили"""
    profiles_list = profile_manager.get_all_profiles()
    return jsonify(profiles_list)

@app.route('/api/profiles', methods=['POST'])
def api_add_profile():
    """API: Добавить новый профиль"""
    try:
        data = request.get_json()
        
        # Валидация обязательных полей
        if not data.get('profile_id') or not data.get('ad_account_id'):
            return jsonify({'error': 'profile_id и ad_account_id обязательны'}), 400
        
        success = profile_manager.add_profile(data)
        if success:
            return jsonify({'message': 'Профиль успешно добавлен'}), 201
        else:
            return jsonify({'error': 'Ошибка при добавлении профиля'}), 500
            
    except Exception as e:
        logger.error(f"Ошибка в API добавления профиля: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/<profile_id>', methods=['PUT'])
def api_update_profile(profile_id):
    """API: Обновить профиль"""
    try:
        data = request.get_json()
        success = profile_manager.update_profile(profile_id, data)
        
        if success:
            return jsonify({'message': 'Профиль успешно обновлен'})
        else:
            return jsonify({'error': 'Ошибка при обновлении профиля'}), 500
            
    except Exception as e:
        logger.error(f"Ошибка в API обновления профиля: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/<profile_id>', methods=['DELETE'])
def api_delete_profile(profile_id):
    """API: Удалить профиль"""
    try:
        success = profile_manager.delete_profile(profile_id)
        
        if success:
            return jsonify({'message': 'Профиль успешно удален'})
        else:
            return jsonify({'error': 'Ошибка при удалении профиля'}), 500
            
    except Exception as e:
        logger.error(f"Ошибка в API удаления профиля: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET'])
def api_get_settings():
    """API: Получить настройки"""
    config = config_manager.get_all()
    # Скрываем чувствительные данные
    config['facebook_access_token'] = '***' if config.get('facebook_access_token') else ''
    return jsonify(config)

@app.route('/api/settings', methods=['POST'])
def api_update_settings():
    """API: Обновить настройки"""
    try:
        data = request.get_json()
        
        # Обновляем конфигурацию
        config_manager.update(data)
        
        return jsonify({'message': 'Настройки успешно обновлены'})
        
    except Exception as e:
        logger.error(f"Ошибка в API обновления настроек: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-collection', methods=['POST'])
def api_run_collection():
    """API: Запустить сбор данных вручную"""
    try:
        # Получаем профили из базы данных
        profiles_list = profile_manager.get_all_profiles()
        active_profiles = [p for p in profiles_list if p.get('is_active', True)]
        
        if not active_profiles:
            return jsonify({'error': 'Нет активных профилей для сбора данных'}), 400
        
        # Преобразуем профили в формат для оркестратора
        config = config_manager.to_legacy_format()
        config['profiles'] = []
        
        for profile in active_profiles:
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
        
        return jsonify({'message': 'Сбор данных успешно запущен'})
        
    except Exception as e:
        logger.error(f"Ошибка при запуске сбора данных: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    """API: Получить статистику"""
    try:
        total_spend_data = db_manager.get_total_spend_by_profile()
        profiles_count = len(profile_manager.get_all_profiles())
        
        stats = {
            'total_profiles': profiles_count,
            'total_spend_data': total_spend_data,
            'last_update': datetime.now().isoformat()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Создаем директории если они не существуют
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Запускаем Flask приложение
    app.run(
        host=config_manager.get('flask_host', '0.0.0.0'),
        port=config_manager.get('flask_port', 5000),
        debug=False
    )

