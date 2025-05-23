
"""
API router configuration.
Конфигурация маршрутизатора API.
"""

from fastapi import APIRouter

from api import payments
from api import external_query

api_router = APIRouter()
api_router.include_router(payments.router, tags=["payments"])
api_router.include_router(external_query.router, tags=["external"])