from fastapi import APIRouter, Query, HTTPException, Response, Header, Depends
import logging
from typing import Optional
from fastapi.responses import StreamingResponse
import io

from services.external_query_service import ExternalQueryService
from models.db_query_result_model import DBQueryResult
from models.format_enum import FormatEnum
from utils.currency.constants import Currency
from utils.formatters import format_data_response
from core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

def verify_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != settings.API_KEY:
        logger.warning(f"Unauthorized access attempt with key: {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

@router.get("/db-query", response_model=list[DBQueryResult])
async def external_query(
    query_name: str = Query(..., description="Имя SQL-скрипта без расширения"),
    format: FormatEnum = Query(FormatEnum.json, description="Response format: json or csv"),
    currency: Currency = Query(Currency.USD, description="Currency for output amounts"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD) for filtering"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD) for filtering"),
    _: None = Depends(verify_api_key)
):
    """
    Выполнить SQL-скрипт из папки SQL_DIR по имени и вернуть результат в формате json или csv.
    """
    try:
        async with ExternalQueryService() as service:
            data = await service.run_query(
                query_name,
                date_from,
                date_to,
                currency.value
            )
        return format_data_response(data, format, f"{query_name}.csv")
    except FileNotFoundError as e:
        logger.warning(f"{e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing query: '{query_name}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
