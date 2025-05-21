from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Payment(BaseModel):
    """
    Модель платежа для сериализации и валидации.
    """
    id: str
    date: datetime
    status: str
    amount: float
    currency: str
    article: str
    sub_article: str
    category: Optional[str] = None
