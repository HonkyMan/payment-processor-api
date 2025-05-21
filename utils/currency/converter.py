"""
Currency converter for converting amounts between different currencies.
Конвертер валют для конвертации сумм между различными валютами.
"""

import logging
from datetime import date
from typing import Dict, Optional, Union, List

from core.config import settings
from utils.currency.client import CurrencyClient
from utils.currency.cache import CurrencyCache

logger = logging.getLogger(__name__)

class CurrencyConverter:
    """Currency converter for converting amounts between different currencies."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize the currency converter.
        
        Args:
            db_path: Path to the SQLite database file
        """
        if db_path is None:
            db_path = settings.SQLITE_DB_PATH
        self.client = CurrencyClient()
        self.cache = CurrencyCache(db_path)
    
    def get_exchange_rates(self, base_currency: str = "usd",
                          request_date: Optional[date] = None) -> Dict[str, float]:
        """
        Get exchange rates with caching.
        
        Args:
            base_currency: Base currency code (e.g., 'usd', 'eur')
            request_date: Date for which to get exchange rates
            
        Returns:
            Dictionary with currency codes as keys and exchange rates as values
        """
        base_currency = base_currency.lower()
        
        # Try to get rates from cache
        cached_rates = self.cache.get_cached_rates(base_currency, request_date)
        
        if cached_rates:
            return cached_rates
        
        # If cache is expired or doesn't exist, fetch new rates
        logger.info(f"Fetching new rates for {base_currency} on {request_date or 'latest'}")
        rates = self.client.get_exchange_rates(base_currency, request_date)
        
        # Save to cache
        self.cache.cache_rates(base_currency, rates, request_date)
        
        return rates
    
    def get_rate(self, from_currency: str, to_currency: str, 
                request_date: Optional[date] = None) -> float:
        """
        Get exchange rate between two currencies.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            request_date: Date for which to get the exchange rate
            
        Returns:
            Exchange rate from source to target currency
            
        Raises:
            ValueError: If the currencies are not found
        """
        from_currency = from_currency.lower()
        to_currency = to_currency.lower()
        
        # If currencies are the same, return 1.0
        if from_currency == to_currency:
            return 1.0
        
        # Get rates with from_currency as base
        rates = self.get_exchange_rates(base_currency=to_currency, request_date=request_date)
        
        if from_currency not in rates:
            raise ValueError(f"Currency {from_currency} not found in exchange rates")
        
        return rates[from_currency]
    
    def convert(self, amount: Union[float, int], from_currency: str, to_currency: str, 
               request_date: Optional[date] = None) -> float:
        """
        Convert amount from one currency to another.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            request_date: Date for which to get the exchange rate
            
        Returns:
            Converted amount in target currency
            
        Raises:
            ValueError: If the currencies are not found
        """
        rate = self.get_rate(from_currency, to_currency, request_date)
        return amount / rate
    
    def convert_many(self, amounts: List[Union[float, int]], from_currency: str, 
                    to_currency: str, request_date: Optional[date] = None) -> List[float]:
        """
        Convert multiple amounts from one currency to another.
        
        Args:
            amounts: List of amounts to convert
            from_currency: Source currency code
            to_currency: Target currency code
            request_date: Date for which to get the exchange rate
            
        Returns:
            List of converted amounts in target currency
            
        Raises:
            ValueError: If the currencies are not found
        """
        rate = self.get_rate(from_currency, to_currency, request_date)
        return [amount * rate for amount in amounts]
