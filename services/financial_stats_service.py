"""
Сервис для выполнения внешних SQL-запросов из файлов.
"""

import os
import logging
from typing import List
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from datetime import date

from core.config import settings
from models.financial_stats_model import FinancialStatsResult
from utils.load_sql_file import load_sql_file
from utils.currency import CurrencyConverter
from utils.currency.constants import Currency, ConversionResult

logger = logging.getLogger(__name__)
SUB_DIR = "/financial"

class FinancialStatsService:
    """
    Сервис для выполнения внешних SQL-запросов из файлов для получения финансовой статистики.
    """
    def __init__(self, database_url: str = None, sql_dir: str = None):
        self.database_url = database_url or settings.DATABASE_URL
        self.sql_dir = sql_dir or settings.SQL_DIR + SUB_DIR
        self.engine: AsyncEngine = create_async_engine(self.database_url, echo=False)
        self.session_factory = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        self.converter = CurrencyConverter()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.converter and self.converter.cache.connection:
            self.converter.cache.connection.close()
            self.converter.cache.connection = None
            logger.debug("Closed currency cache connection")
        await self.engine.dispose()

    def _parse_date(self, s: str) -> date:
        try:
            return date.fromisoformat(s)
        except Exception:
            return None

    async def run_query(self, query_name: str, date_from: str = None, date_to: str = None, currency: str = "USD") -> List[FinancialStatsResult]:
        query = load_sql_file(self.sql_dir, query_name)

        params = {
            "date_from": self._parse_date(date_from) if date_from else None,
            "date_to": self._parse_date(date_to) if date_to else None
        }

        financial_data: List[FinancialStatsResult] = []
        target_currency = (currency or "USD").upper()

        try:
            async with self.session_factory() as session:
                try:
                    result = await session.execute(sqlalchemy.text(query), params)
                    records = [dict(r) for r in result.mappings()]
                    logger.info(f"Executed query '{query_name}', returned {len(records)} rows")
                    for row in records:
                        row_currency = row["currency"].upper()
                        amount = float(row["amount"])
                        date_val = row["date"]
                        try:
                            if row_currency != target_currency:
                                conv_result: ConversionResult = self.converter.safe_convert(
                                    amount=amount,
                                    from_currency=row_currency,
                                    to_currency=target_currency,
                                    request_date=date_val,
                                    default_value=amount
                                )
                                amount = conv_result.converted_amount
                                row_currency = conv_result.to_currency.value
                                logger.debug(f"Converted amount: {conv_result}")
                            financial_data.append(FinancialStatsResult(
                                date=date_val,
                                amount=round(amount, 2),
                                currency=row_currency
                            ))
                        except Exception as e:
                            logger.error(f"Currency conversion error for row {row}: {e}")
                            financial_data.append(FinancialStatsResult(
                                date=date_val,
                                amount=round(amount, 2),
                                currency=row_currency
                            ))
                except Exception as e:
                    logger.error(f"Database error executing query '{query_name}': {e}")
                    raise
        finally:
            if self.converter and self.converter.cache.connection:
                self.converter.cache.connection.close()
                self.converter.cache.connection = None
                logger.debug("Closed currency cache connection")
        logger.info(f"Successfully executed query '{query_name}' with {len(financial_data)} records")
        return financial_data
