from typing import List
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import pandas as pd
import io

from models.format_enum import FormatEnum


def format_data_response(
    data: List[BaseModel],
    fmt: FormatEnum,
    filename: str
):
    """
    Форматирует результат в JSON или CSV.
    - fmt == FormatEnum.json: возвращает list модели (FastAPI сериализует в JSON).
    - fmt == FormatEnum.csv: возвращает StreamingResponse с CSV-данными.

    Args:
        data: Список Pydantic-моделей
        fmt: Формат (json или csv)
        filename: Имя файла для CSV

    Returns:
        JSON или CSV StreamingResponse
    """
    if fmt == FormatEnum.json:
        return data
    # CSV
    df = pd.DataFrame([item.model_dump() for item in data])
    csv_str = df.to_csv(index=False)
    return StreamingResponse(
        io.StringIO(csv_str),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
