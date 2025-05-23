"""
Currency converter for converting amounts between different currencies.
Конвертер валют для конвертации сумм между различными валютами.
"""

import logging
from datetime import date
from typing import Dict, Optional, Union, List, Tuple

from core.config import settings
from utils.currency.client import CurrencyClient
from utils.currency.cache import CurrencyCache
from utils.currency.constants import Currency, ConversionResult

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
    
    def get_exchange_rates(self, base_currency: Union[Currency, str] = Currency.USD,
                          request_date: Optional[date] = None) -> Dict[str, float]:
        """
        Get exchange rates with caching.
        
        Args:
            base_currency: Base currency code (e.g., Currency.USD, Currency.EUR)
            request_date: Date for which to get exchange rates
            
        Returns:
            Dictionary with currency codes as keys and exchange rates as values
        """
        if isinstance(base_currency, Currency):
            base_currency = base_currency.value.lower()
        else:
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
    
    def get_rate(self, from_currency: Union[Currency, str], to_currency: Union[Currency, str], 
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
        if isinstance(from_currency, Currency):
            from_currency = from_currency.value.lower()
        else:
            from_currency = from_currency.lower()
            
        if isinstance(to_currency, Currency):
            to_currency = to_currency.value.lower()
        else:
            to_currency = to_currency.lower()
        
        # If currencies are the same, return 1.0
        if from_currency == to_currency:
            return 1.0
        
        # Get rates with from_currency as base
        rates = self.get_exchange_rates(base_currency=to_currency, request_date=request_date)
        
        if from_currency not in rates:
            raise ValueError(f"Currency {from_currency} not found in exchange rates")
        
        return rates[from_currency]
    
    def convert(self, amount: Union[float, int], from_currency: Union[Currency, str], 
                to_currency: Union[Currency, str], request_date: Optional[date] = None) -> float:
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
        converted = amount / rate
        return round(converted, 2)
    
    def convert_many(self, amounts: List[Union[float, int]], from_currency: Union[Currency, str], 
                    to_currency: Union[Currency, str], request_date: Optional[date] = None) -> List[float]:
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
        return [round(amount * rate, 2) for amount in amounts]

    def safe_convert(self, amount: Union[float, int], from_currency: Union[Currency, str],
                    to_currency: Union[Currency, str], request_date: Optional[date] = None,
                    default_value: Optional[float] = None) -> ConversionResult:
        """
        Safely convert amount between currencies with detailed result and error handling.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency 
            to_currency: Target currency
            request_date: Date for exchange rate (optional)
            default_value: Value to return if conversion fails (optional)
            
        Returns:
            ConversionResult with conversion details and resulting amount
            
        Example:
            >>> converter = CurrencyConverter()
            >>> result = converter.safe_convert(100, Currency.USD, Currency.EUR)
            >>> print(result.converted_amount)  # 92.34
            >>> print(result)  # "100 USD = 92.34 EUR (rate: 0.9234 on 2024-04-01)"
        """
        try:
            # Normalize currencies
            if isinstance(from_currency, str):
                from_currency = Currency(from_currency.upper())
            if isinstance(to_currency, str):
                to_currency = Currency(to_currency.upper())

            # Get conversion rate
            rate = self.get_rate(from_currency, to_currency, request_date)
            converted_amount = round(amount / rate, 2)

            return ConversionResult(
                original_amount=amount,
                converted_amount=converted_amount,
                from_currency=from_currency,
                to_currency=to_currency,
                conversion_date=request_date,
                rate=rate
            )
        except (ValueError, KeyError) as e:
            logger.error(f"Currency conversion error: {e}")
            if default_value is not None:
                return ConversionResult(
                    original_amount=amount,
                    converted_amount=default_value,
                    from_currency=from_currency if isinstance(from_currency, Currency) else Currency.USD,
                    to_currency=to_currency if isinstance(to_currency, Currency) else Currency.USD,
                    conversion_date=request_date,
                    rate=1.0
                )
            raise
