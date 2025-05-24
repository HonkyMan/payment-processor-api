import os
import logging
from datetime import date
from typing import List, Optional
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine

from core.config import settings
from utils.load_sql_file import load_sql_file
from models.user_activity_model import ActiveUsersResult

logger = logging.getLogger(__name__)
SUB_DIR = "/activity"

class UserActivityService:
    """
    Сервис для выполнения внешних SQL-запросов из файлов для получения статистику по активности.
    """
    def __init__(self, database_url: str = None, sql_dir: str = None):
        self.database_url = database_url or settings.DATABASE_URL
        self.sql_dir = sql_dir or settings.SQL_DIR + SUB_DIR
        self.engine: AsyncEngine = create_async_engine(self.database_url, echo=False)
        self.session_factory = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    def _parse_date(self, s: str) -> date:
        try:
            return date.fromisoformat(s)
        except Exception:
            return None

    async def get_active_users(
        self,
        query_name: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[ActiveUsersResult]:
        
        query = load_sql_file(self.sql_dir, query_name)

        params = {
            "date_from": self._parse_date(date_from) if date_from else None,
            "date_to": self._parse_date(date_to) if date_to else None
        }

        activity_data: List[ActiveUsersResult] = []

        async with self.session_factory() as session:
            try:
                result = await session.execute(sqlalchemy.text(query), params)
                records = [dict(r) for r in result.mappings()]

                logger.info(f"Executed query '{query_name}', returned {len(records)} rows")

                for row in records:
                    activity_data.append(ActiveUsersResult(
                        date=row["date"],
                        active_users=int(row["active_users"])
                    ))
            except Exception as e:
                logger.error(f"Database error executing query '{query_name}': {e}")
                raise

        return activity_data
