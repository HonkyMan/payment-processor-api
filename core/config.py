"""
Configuration settings for the application.
Настройки конфигурации приложения.
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # Основные настройки приложения
    PROJECT_NAME: str = "Payment Processor API"
    PROJECT_DESCRIPTION: str = "API для обработки платежей из CSV файлов"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    API_PREFIX: str = "/api/v1"
    
    # Настройки CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Настройки базы данных SQLite для кэширования курсов валют
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "exchange_rates.db")
    
    # Настройки API курсов валют
    EXCHANGE_RATE_API_URL: str = os.getenv("EXCHANGE_RATE_API_URL", "https://api.exchangerate-api.com/v4/latest/USD")
    
    # Путь к файлу с таблицей соответствия категорий
    CATEGORY_MAPPING_PATH: str = os.getenv("CATEGORY_MAPPING_PATH", "data/category_mapping.json")
    
    # Путь к файлу по умолчанию для платежей Aya
    PAYMENTS_FILE_PATH: str = os.getenv("PAYMENTS_FILE_PATH", "data/pay.aya.csv")
    
    # Статус успешного платежа
    PAYMENT_SUCCESS_STATUS: str = os.getenv("PAYMENT_SUCCESS_STATUS", "Оплачено")
    
    # API ключ для авторизации
    API_KEY: str = os.getenv("API_KEY", "changeme")
    # URL для подключения к удалённой БД
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    # Папка со SQL-скриптами
    SQL_DIR: str = os.getenv("SQL_DIR", "sql")

    class Config:
        env_file = ".env"
        case_sensitive = True

# Создание экземпляра настроек
settings = Settings()
