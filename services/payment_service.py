from typing import List, Optional
import pandas as pd
import logging
from utils.csv_processor import CSVProcessor
from utils.category_mapper import map_category
from utils.currency import CurrencyConverter
from utils.currency.constants import Currency, ConversionResult
from core.config import settings
from models.payment_model import Payment
from datetime import datetime

logger = logging.getLogger(__name__)

class PaymentService:
    """
    Сервис для обработки платежей из CSV-файла.
    """
    def __init__(self, file_path: Optional[str]):
        self.file_path: str = file_path or settings.PAYMENTS_FILE_PATH
        self.processor: CSVProcessor = CSVProcessor(self.file_path)
        logger.info(f"PaymentService initialized with file: {self.file_path}")

    def process_payments(self, target_currency: str = "USD", date_from: Optional[str] = None, date_to: Optional[str] = None) -> List[Payment]:
        logger.info(f"Start processing payments. Target currency: {target_currency}, date_from: {date_from}, date_to: {date_to}")
        self.processor.read_csv()
        required_columns: List[str] = ["id", "Дата", "Статус", "Сумма", "Валюта", "Статья", "Подстатья"]
        processed_data: pd.DataFrame = self.processor.prepare_data(
            required_columns=required_columns,
            status=settings.PAYMENT_SUCCESS_STATUS,
            date_from=date_from,
            date_to=date_to
        )

        # Категории
        article_columns: List[str] = [col for col in processed_data.columns if col.lower() in ["article", "статья"]]
        sub_article_columns: List[str] = [col for col in processed_data.columns if col.lower() in ["sub_article", "sub-article", "подстатья"]]
        if article_columns and sub_article_columns:
            article_col = article_columns[0]
            sub_article_col = sub_article_columns[0]
            processed_data["category"] = processed_data.apply(
                lambda row: map_category(str(row[article_col]), str(row[sub_article_col])), axis=1
            )
            logger.info("Categories mapped for payments.")

        # Конвертация валюты
        amount_columns: List[str] = [col for col in processed_data.columns if col.lower() in ["amount", "сумма"]]
        currency_columns: List[str] = [col for col in processed_data.columns if col.lower() in ["currency", "валюта"]]
        date_columns: List[str] = [col for col in processed_data.columns if col.lower() in ["date", "дата"]]
        
        converter = None
        try:
            if amount_columns and currency_columns and date_columns:
                amount_col = amount_columns[0]
                currency_col = currency_columns[0]
                date_col = date_columns[0]
                
                # Создаем конвертер один раз для всех операций
                converter = CurrencyConverter()
                
                for idx, row in processed_data.iterrows():
                    source_currency = str(row[currency_col]).upper()
                    if source_currency != target_currency:
                        try:
                            result: ConversionResult = converter.safe_convert(
                                amount=float(row[amount_col]),  # Преобразуем в float для конвертации
                                from_currency=source_currency,
                                to_currency=target_currency,
                                request_date=row[date_col],
                                default_value=float(row[amount_col])  # если конвертация не удалась, оставляем исходную сумму
                            )
                            processed_data.at[idx, amount_col] = result.converted_amount
                            processed_data.at[idx, currency_col] = result.to_currency.value
                            logger.debug(f"Converted payment: {result}")
                        except Exception as e:
                            logger.error(f"Currency conversion error for row {idx}: {e}")
                            # Оставляем исходные значения
                            continue
                            
            logger.info(f"Total processed payments: {len(processed_data)}")

            # Формируем список моделей Payment
            payments: List[Payment] = [
                Payment(
                    id=str(row["id"]),
                    date=row["Дата"],
                    status=row["Статус"],
                    amount=round(row["Сумма"], 2),
                    currency=row["Валюта"],
                    article=row["Статья"],
                    sub_article=row["Подстатья"],
                    category=row.get("category", None)
                )
                for _, row in processed_data.iterrows()
            ]
            logger.info(f"Successfully created {len(payments)} Payment models.")
            return payments

        finally:
            # Закрываем соединение с кэшем, если конвертер был создан
            if converter and converter.cache.connection:
                converter.cache.connection.close()
                converter.cache.connection = None
                logger.debug("Closed currency cache connection")
