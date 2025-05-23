"""
SQLite cache for currency exchange rates.
SQLite кэш для курсов валют.
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class CurrencyCache:
    """SQLite cache for currency exchange rates."""
    
    def __init__(self, db_path: str = "data/exchange_rates.db"):
        """
        Initialize the currency cache.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self._init_db()
        self._get_connection()
            
    def _get_connection(self) -> sqlite3.Connection:
        """Получить активное соединение или создать новое"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def _init_db(self):
        """Initialize the database for caching exchange rates."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            
        try:
            conn = self._get_connection()
            
            # Создаем таблицу, если её нет
            conn.execute('''
                CREATE TABLE IF NOT EXISTS currency_rates (
                    base_currency TEXT,
                    date TEXT,
                    rates TEXT,
                    timestamp TEXT,
                    PRIMARY KEY (base_currency, date)
                )
            ''')
            conn.commit()
            
            # Проверяем, что таблица создана
            cursor = conn.execute("""
                SELECT name FROM sqlite_master WHERE type='table' AND name='currency_rates';
            """)
            if cursor.fetchone():
                logger.info("Table 'currency_rates' exists in DB.")
            else:
                logger.warning("Failed to create currency_rates table!")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            if self.connection:
                self.connection.close()
                self.connection = None
    
    def get_cached_rates(self, base_currency: str, 
                         request_date: date) -> Optional[Dict[str, float]]:
        """
        Get exchange rates from cache.
        
        Args:
            base_currency: Base currency code (e.g., 'usd', 'eur')
            request_date: Date for which to get exchange rates
            
        Returns:
            Dictionary with currency codes as keys and exchange rates as values,
            or None if the cache is expired or doesn't exist
        """
        date_str = request_date.strftime("%Y-%m-%d")
        
        try:
            conn = self._get_connection()
            cursor = conn.execute(
                "SELECT rates FROM currency_rates WHERE base_currency = ? AND date = ?",
                (base_currency.lower(), date_str)
            )
            row = cursor.fetchone()
            
            if row:
                rates = json.loads(row['rates'])
                return rates
            
            return None
        except Exception as e:
            logger.error(f"Error retrieving cached rates: {e}")
            if self.connection:
                self.connection.close()
                self.connection = None
            return None
    
    def cache_rates(self, base_currency: str, rates: Dict[str, float], 
                   request_date: date = None):
        """
        Save exchange rates to cache.
        
        Args:
            base_currency: Base currency code (e.g., 'usd', 'eur')
            rates: Dictionary with currency codes as keys and exchange rates as values
            request_date: Date for which the rates are valid
        """
        date_str = request_date.strftime("%Y-%m-%d")
        
        try:
            conn = self._get_connection()
            conn.execute(
                """
                INSERT OR REPLACE INTO currency_rates (base_currency, date, rates, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (
                    base_currency.lower(),
                    date_str,
                    json.dumps(rates),
                    datetime.now().isoformat()
                )
            )
            conn.commit()
            logger.debug(f"Cached rates for {base_currency} on {date_str}")
        except Exception as e:
            logger.error(f"Error caching rates: {e}")
            if self.connection:
                self.connection.close()
                self.connection = None
