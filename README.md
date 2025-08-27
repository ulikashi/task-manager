# Task Manager API (FastAPI + PostgreSQL + JWT)

Проект демонстрирует: FastAPI (async), SQLAlchemy 2.0, JWT (access/refresh) с ротацией и отзывом, роли (user/admin), Docker Compose и автотесты.

## Быстрый старт (локально)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
# пример строки подключения для быстрого старта без Postgres:
# DATABASE_URL=sqlite+aiosqlite:///./dev.db
uvicorn app.main:app --reload