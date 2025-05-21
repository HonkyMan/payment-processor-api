# Payment Processor API

## Описание

REST API для обработки CSV-файлов с платежами, конвертации валют, маппинга категорий и выгрузки данных в формате JSON или CSV.

- Поддержка загрузки и обработки платежей из CSV
- Конвертация валют с кэшированием курсов
- Маппинг "Статья" + "Подстатья" в бизнес-категории
- Гибкая настройка через .env
- Эндпоинты для healthcheck и получения платежей

## Быстрый старт

1. Клонируйте репозиторий и перейдите в папку src:
   ```sh
   cd src
   ```
2. Установите зависимости:
   ```sh
   pip install -r app/requirements.txt
   ```
3. Запустите сервер:
   ```sh
   uvicorn app.main:app --reload
   ```
4. Откройте документацию: [http://localhost:8000/docs](http://localhost:8000/docs)

## Основные эндпоинты

- `GET /api/v1/payments` — получить обработанные платежи (json/csv)
- `GET /api/v1/healthcheck` — проверка работоспособности

## Пример запроса

```sh
curl "http://localhost:8000/api/v1/payments?format=json&currency=USD"
```

## Переменные окружения (.env)

- `PAYMENTS_FILE_PATH` — путь к файлу с платежами по умолчанию
- `CATEGORY_MAPPING_PATH` — путь к json-файлу с маппингом категорий
- `SQLITE_DB_PATH` — путь к базе для кэша курсов валют
- `EXCHANGE_RATE_API_URL` — url для получения курсов валют
- `EXCHANGE_RATE_CACHE_TTL` — время жизни кэша курсов валют (часы)
- `PAYMENT_SUCCESS_STATUS` — статус успешного платежа (например, "Оплачено")

## Структура проекта

- `api/` — роуты FastAPI
- `services/` — бизнес-логика
- `models/` — pydantic-модели
- `utils/` — утилиты (конвертер валют, маппер категорий, обработка CSV)
- `data/` — файлы данных (csv, json, db)
- `core/` — конфиг и настройки