import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.service.event_svc import EventService
from app.service.notification_svc import NotificationService
from app.routers.events import router as events_router
from app.store import InMemoryEventStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Инициализирует сервисы приложения в app.state.
    store = InMemoryEventStore()
    notification_service: NotificationService = NotificationService()
    app.state.store = store
    app.state.generator = notification_service
    app.state.event_service = EventService(
        store=store,
        notification_generator=notification_service,
    )
    yield


app = FastAPI(title="Event Notify Service", version="0.1.0", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    # Возвращает ошибку валидации на русском языке.
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Некорректные входные данные.",
            "errors": exc.errors(),
        },
    )


app.include_router(events_router)
