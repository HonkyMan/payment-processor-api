from fastapi import Header, HTTPException
from core.config import settings
import logging

logger = logging.getLogger(__name__)

def verify_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != settings.API_KEY:
        logger.warning(f"Unauthorized access attempt with key: {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
