"""
API endpoints for processing payment data.
API эндпоинты для обработки платежных данных.
"""

import os
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Response, Header, Depends
from fastapi.responses import StreamingResponse
import logging

from services.payment_service import PaymentService
from models.payment_model import Payment
from models.format_enum import FormatEnum
from utils.currency.constants import Currency
from core.config import settings
from utils.formatters import format_data_response

router = APIRouter()
logger = logging.getLogger(__name__)

def verify_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != settings.API_KEY:
        logger.warning(f"Unauthorized access attempt with key: {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

@router.get("/payments", response_model=List[Payment])
async def get_payments(
    file_path: Optional[str] = Query(None, description="Path to the CSV file with payment data"),
    format: FormatEnum = Query(FormatEnum.json, description="Response format (json or csv)"),
    currency: Currency = Query(Currency.USD, description="Currency for payment amounts"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD) for filtering payments"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD) for filtering payments"),
    _: None = Depends(verify_api_key)
) -> List[Payment]:
    """
    Process payment data from a CSV file and return it in the specified format and currency.
    Если file_path не передан, используется путь из settings.PAYMENTS_FILE_PATH.
    Фильтрация по дате: date_from/date_to в формате YYYY-MM-DD.
    """
    if not file_path:
        file_path = settings.PAYMENTS_FILE_PATH
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    try:
        service = PaymentService(file_path)
        payments = service.process_payments(
            target_currency=currency.value,
            date_from=date_from,
            date_to=date_to
        )
        return format_data_response(payments, format, "payments.csv")
    except Exception as e:
        logger.error(f"Error processing payment data: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing payment data: {str(e)}")
