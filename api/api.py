"""
API router configuration.
Конфигурация маршрутизатора API.
"""

from fastapi import APIRouter

from api import payments
from api import financial
from api import activities

api_router = APIRouter()
api_router.include_router(payments.router, tags=["payments"])
api_router.include_router(financial.router, tags=["db-queries"])
api_router.include_router(activities.router, tags=["db-queries"])