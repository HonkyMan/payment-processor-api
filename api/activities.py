from fastapi import APIRouter, Query, HTTPException, Depends
import logging
from typing import Optional, List
from fastapi.responses import StreamingResponse
import io

from services.user_activity_service import UserActivityService
from models.user_activity_model import ActiveUsersResult
from models.format_enum import FormatEnum
from utils.formatters import format_data_response
from core.auth import verify_api_key

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/user-activity", response_model=List[ActiveUsersResult])
async def get_user_activity(
    query_name: str = Query(..., description="Имя SQL-скрипта без расширения"),
    format: FormatEnum = Query(FormatEnum.json, description="Response format: json or csv"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD) for filtering"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD) for filtering"),
    _: None = Depends(verify_api_key)
):
    """
    Получить данные о ежедневной активности пользователей.
    """
    try:
        service = UserActivityService()
        results = await service.get_active_users(
            query_name,
            date_from,
            date_to
        )
        return format_data_response(
            data=results,
            fmt=format,
            filename=f"{query_name}.csv"
        )
    except Exception as e:
        logger.error(f"Error getting user activity data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
