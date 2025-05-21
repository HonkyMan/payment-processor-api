"""
Client for fetching currency exchange rates from external API.
Клиент для получения курсов валют из внешнего API.
"""

import requests
import logging
from datetime import datetime, date
from typing import Dict, Optional, Any
from core.config import settings

logger = logging.getLogger(__name__)

class CurrencyClient:
    """Client for fetching currency exchange rates from external API."""
    
    BASE_URL = settings.EXCHANGE_RATE_API_URL # https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2024-04-01/v1/currencies/usd.json
    LATEST_AVAILABLE_DATE = date(2024, 4, 1)  # API data is only available until 2024-04-01
    
    def __init__(self):
        """Initialize the currency client."""
        self.session = requests.Session()
    
    def _get_api_url(self, base_currency: str, request_date: Optional[date] = None) -> str:
        """
        Get the API URL for the specified base currency and date.
        
        Args:
            base_currency: Base currency code (e.g., 'usd', 'eur')
            request_date: Date for which to get exchange rates
            
        Returns:
            URL for the API request
        """
        # If no date is provided or the date is after the latest available date,
        # use the latest available date
        if request_date is None:
            date_str = self.LATEST_AVAILABLE_DATE.strftime("%Y-%m-%d")
        else:
            # Привести request_date к типу date, если это pandas.Timestamp
            if hasattr(request_date, 'date'):
                request_date_cmp = request_date.date()
            else:
                request_date_cmp = request_date
            if request_date_cmp < self.LATEST_AVAILABLE_DATE:
                date_str = self.LATEST_AVAILABLE_DATE.strftime("%Y-%m-%d")
            else:
                date_str = request_date.strftime("%Y-%m-%d")
        return self.BASE_URL.format(date=date_str, base=base_currency.lower())
    
    def get_exchange_rates(self, base_currency: str, request_date: date) -> Dict[str, float]:
        """
        Fetch exchange rates from the API.
        
        Args:
            base_currency: Base currency code (e.g., 'usd', 'eur')
            request_date: Date for which to get exchange rates
            
        Returns:
            Dictionary with currency codes as keys and exchange rates as values
            
        Raises:
            ValueError: If the API request fails
        """
        if not base_currency or not request_date:
            raise ValueError("Base currency and request date must be provided for client request")
        
        url = self._get_api_url(base_currency, request_date)
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # The API returns data in format {base_currency: {currency_code: rate, ...}}
            if base_currency.lower() in data:
                return data[base_currency.lower()]
            else:
                logger.error(f"Unexpected API response format: {data}")
                raise ValueError(f"Unexpected API response format")
                
        except requests.RequestException as e:
            logger.error(f"Error fetching exchange rates: {e}")
            raise ValueError(f"Failed to fetch exchange rates: {str(e)}")
        except ValueError as e:
            logger.error(f"Error parsing exchange rates: {e}")
            raise ValueError(f"Failed to parse exchange rates: {str(e)}")
