-- init.sql
-- Скрипт инициализации базы данных PostgreSQL

-- Создание таблицы профилей
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
);

-- Создание таблицы данных о расходах на рекламу
CREATE TABLE IF NOT EXISTS ad_spend (
    id SERIAL PRIMARY KEY,
    profile_id VARCHAR(255) NOT NULL,
    ad_account_id VARCHAR(255) NOT NULL,
    ad_id VARCHAR(255),
    ad_name TEXT,
    campaign_id VARCHAR(255),
    campaign_name TEXT,
    adset_id VARCHAR(255),
    adset_name TEXT,
    date_start DATE NOT NULL,
    date_stop DATE NOT NULL,
    spend DECIMAL(10,2) DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    ctr DECIMAL(5,4) DEFAULT 0,
    cpc DECIMAL(10,2) DEFAULT 0,
    cpm DECIMAL(10,2) DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(profile_id, ad_account_id, ad_id, date_start, date_stop)
);

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_ad_spend_profile_id ON ad_spend(profile_id);
CREATE INDEX IF NOT EXISTS idx_ad_spend_ad_account_id ON ad_spend(ad_account_id);
CREATE INDEX IF NOT EXISTS idx_ad_spend_date_start ON ad_spend(date_start);
CREATE INDEX IF NOT EXISTS idx_ad_spend_date_stop ON ad_spend(date_stop);
CREATE INDEX IF NOT EXISTS idx_profiles_profile_id ON profiles(profile_id);
CREATE INDEX IF NOT EXISTS idx_profiles_is_active ON profiles(is_active);

-- Вставка тестовых данных (опционально)
INSERT INTO profiles (profile_id, ad_account_id, currency, is_active) 
VALUES 
    ('test-profile-1', '123456789', 'USD', true),
    ('test-profile-2', '987654321', 'EUR', false)
ON CONFLICT (profile_id) DO NOTHING;

