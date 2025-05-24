from pydantic import BaseModel
from datetime import date
from utils.currency.constants import Currency

class FinancialStatsResult(BaseModel):
    """
    Модель результата выполнения SQL-запроса для endpoint db-query.
    Поля соответствуют столбцам SQL-файлов: date и amount.
    """
    date: date
    amount: float
    currency: Currency
