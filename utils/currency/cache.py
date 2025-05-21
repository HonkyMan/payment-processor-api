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
        self._init_db()
    
    def _init_db(self):
        """Initialize the database for caching exchange rates."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        db_exists = os.path.exists(self.db_path)
        if not db_exists:
            logger.info(f"Currency cache DB will be created: {self.db_path}")
            with sqlite3.connect(self.db_path) as conn:
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
        else:
            logger.info(f"Currency cache DB already exists: {self.db_path}")
            # Проверяем, что таблица currency_rates есть
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master WHERE type='table' AND name='currency_rates';
                """)
                result = cursor.fetchone()
                if result:
                    logger.info("Table 'currency_rates' exists in DB.")
                else:
                    logger.warning("Table 'currency_rates' NOT found in DB. Creating table...")
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
                    logger.info("Table 'currency_rates' created in existing DB.")
    
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
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
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
            with sqlite3.connect(self.db_path) as conn:
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
