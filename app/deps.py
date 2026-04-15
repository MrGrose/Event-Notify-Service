from fastapi import Request

from app.service.event_svc import EventService
from app.service.notification_svc import NotificationService
from app.store import InMemoryEventStore


def get_store(request: Request) -> InMemoryEventStore:
    # Возвращает in-memory хранилище событий из состояния приложения.
    return request.app.state.store


def get_generator(request: Request) -> NotificationService:
    # Возвращает уведомлений из состояния приложения.
    return request.app.state.generator


def get_event_service(request: Request) -> EventService:
    # Возвращает сервис обработки событий из состояния приложения.
    return request.app.state.event_service
