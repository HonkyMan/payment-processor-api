# Используем официальный образ Python как базовый
FROM python:3.13-alpine

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости для сборки Python-пакетов
RUN apk add --no-cache gcc musl-dev libffi-dev build-base

# Копируем файлы зависимостей
COPY requirements.txt ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение внутрь контейнера
COPY . .

# Переменная окружения для предотвращения буферизации вывода Python
ENV PYTHONUNBUFFERED=1

# Открываем порт для FastAPI
EXPOSE 8000

# Команда запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
