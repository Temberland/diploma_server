#!/bin/bash
set -e

echo "Применяем миграции..."
alembic upgrade head

echo "Запускаем сервер..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
