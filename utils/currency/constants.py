"""
Constants and types for currency operations.
Константы и типы для операций с валютами.
"""
from enum import Enum
from typing import Optional
from datetime import date
from pydantic import BaseModel


class Currency(str, Enum):
    """
    Supported currencies.
    Поддерживаемые валюты.
    """
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"
    UZS = "UZS"
    USDT = "USDT"
    INR = "INR"
    TON = "TON"


class ConversionResult(BaseModel):
    """
    Result of currency conversion operation.
    Результат операции конвертации валюты.
    """
    original_amount: float
    converted_amount: float
    from_currency: Currency
    to_currency: Currency
    conversion_date: Optional[date]
    rate: float

    def __str__(self) -> str:
        return (
            f"{self.original_amount} {self.from_currency} = "
            f"{self.converted_amount} {self.to_currency}"
            f" (rate: {self.rate} on {self.conversion_date or 'latest'})"
        )
