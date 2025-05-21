"""
API endpoints for processing payment data.
API эндпоинты для обработки платежных данных.
"""

import os
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Response, Header, Depends
from fastapi.responses import JSONResponse, StreamingResponse
import io
import logging

from services.payment_service import PaymentService
from models.payment import Payment
from core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

def verify_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != settings.API_KEY:
        logger.warning(f"Unauthorized access attempt with key: {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

@router.get("/payments", response_model=List[Payment])
async def get_payments(
    file_path: Optional[str] = Query(None, description="Path to the CSV file with payment data"),
    format: Optional[str] = Query("json", description="Response format (json or csv)"),
    currency: Optional[str] = Query("USD", description="Currency for payment amounts"),
    _: None = Depends(verify_api_key)
) -> List[Payment]:
    """
    Process payment data from a CSV file and return it in the specified format and currency.
    Если file_path не передан, используется путь из settings.PAYMENTS_FILE_PATH.
    """
    if not file_path:
        file_path = settings.PAYMENTS_FILE_PATH
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    format = format.lower()
    if format not in ["json", "csv"]:
        logger.error(f"Invalid format: {format}")
        raise HTTPException(status_code=400, detail=f"Invalid format: {format}. Supported formats: json, csv")
    currency = currency.upper()
    try:
        service = PaymentService(file_path)
        payments = service.process_payments(target_currency=currency)
        if format == "json":
            return payments
        elif format == "csv":
            import pandas as pd
            df = pd.DataFrame([p.model_dump() for p in payments])
            csv_data = df.to_csv(index=False)
            return StreamingResponse(
                io.StringIO(csv_data),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=payments.csv"}
            )
        else:
            logger.error("Unsupported format. Use 'json' or 'csv'.")
            raise HTTPException(status_code=400, detail="Unsupported format. Use 'json' or 'csv'.")
    except Exception as e:
        logger.error(f"Error processing payment data: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing payment data: {str(e)}")
