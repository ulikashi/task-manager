from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_models
from .routers import auth, tasks, users

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Разрешаем запросы со всех источников (для dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    # создаём таблицы, если их нет
    await init_models()

# Подключение роутеров
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)

# healthcheck
@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "app": settings.APP_NAME}