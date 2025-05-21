
"""
API router configuration.
Конфигурация маршрутизатора API.
"""

from fastapi import APIRouter

from api import payments

api_router = APIRouter()
api_router.include_router(payments.router, tags=["payments"])