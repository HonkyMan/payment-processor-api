# Payment & Analytics API

## Описание

Асинхронный REST API для работы с платежами, аналитикой и пользовательской активностью. Поддерживает загрузку и обработку CSV-файлов, выполнение SQL-отчетов, конвертацию валют, бизнес-маппинг категорий, а также выгрузку данных в форматах JSON и CSV.

**Возможности:**
- Загрузка и обработка платежей из CSV
- Конвертация валют с кэшированием курсов (SQLite)
- Маппинг "Статья" + "Подстатья" в бизнес-категории
- Выполнение внешних SQL-отчетов по финансовым и пользовательским метрикам
- Эндпоинты для статистики активности пользователей
- Гибкая настройка через .env
- Асинхронная работа с PostgreSQL через SQLAlchemy
- Валидация валюты и формата ответа через Enum
- Единый стиль сервисов (только классы, поддержка контекстных менеджеров)
- Эндпоинты для healthcheck и получения платежей

## Быстрый старт

1. Клонируйте репозиторий и перейдите в папку src/app:
   ```sh
   cd src/app
   ```
2. Установите зависимости:
   ```sh
   pip install -r requirements.txt
   ```
3. Запустите сервер:
   ```sh
   uvicorn main:app --reload
   ```
4. Откройте документацию: [http://localhost:8000/docs](http://localhost:8000/docs)

## Основные эндпоинты

- `GET /api/v1/payments` — получить обработанные платежи (json/csv, с конвертацией валют)
- `GET /api/v1/financial-stats` — финансовая аналитика по SQL-отчетам (json/csv, фильтрация по дате и валюте)
- `GET /api/v1/user-activity` — статистика активности пользователей (json/csv, фильтрация по дате)
- `GET /api/v1/healthcheck` — проверка работоспособности

## Примеры запросов

```sh
curl "http://localhost:8000/api/v1/payments?format=json&currency=USD"
curl "http://localhost:8000/api/v1/financial-stats?query_name=stakes_sport_amount&currency=EUR&date_from=2024-01-01&date_to=2024-01-31"
curl "http://localhost:8000/api/v1/user-activity?query_name=active_users&format=csv&date_from=2024-01-01&date_to=2024-01-31"
```

## Переменные окружения (.env)

- `PAYMENTS_FILE_PATH` — путь к файлу с платежами по умолчанию
- `CATEGORY_MAPPING_PATH` — путь к json-файлу с маппингом категорий
- `SQLITE_DB_PATH` — путь к базе для кэша курсов валют
- `EXCHANGE_RATE_API_URL` — url для получения курсов валют
- `EXCHANGE_RATE_CACHE_TTL` — время жизни кэша курсов валют (часы)
- `PAYMENT_SUCCESS_STATUS` — статус успешного платежа (например, "Оплачено")
- `DATABASE_URL` — строка подключения к PostgreSQL
- `SQL_DIR` — папка с SQL-скриптами (например, data/sql)
- `API_KEY` — ключ для авторизации

## Структура проекта

- `api/` — роуты FastAPI (payments, financial, activities, api)
- `services/` — бизнес-логика (payment_service, financial_stats_service, user_activity_service)
- `models/` — pydantic-модели и enum (payment_model, financial_stats_model, user_activity_model, format_enum)
- `utils/` — утилиты (конвертер валют, маппер категорий, обработка CSV, форматтеры, загрузка SQL)
- `data/` — файлы данных (csv, json, db, sql-скрипты)
- `core/` — конфиг и авторизация

## Особенности архитектуры

- Все сервисы реализованы как полноценные классы с управлением ресурсами (через контекстные менеджеры)
- Конвертация валют и кэширование курсов унифицированы для всех сервисов
- Валидация валюты и формата ответа через Enum
- Асинхронная работа с базой данных и SQLAlchemy
- Чистая структура и единый стиль кода
- SQL-запросы вынесены в отдельные файлы для прозрачности и удобства сопровождения