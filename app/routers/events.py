import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_event_service, get_store
from app.service.event_svc import EventService
from app.models import (
    EventAcceptedResponse,
    EventRecord,
    EventRejectedResponse,
    EventRequest,
)
from app.store import InMemoryEventStore

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/events", 
    response_model=list[EventRecord], 
    summary="Получить сохраненные события",
)
async def get_events(
    store: InMemoryEventStore = Depends(get_store),
) -> list[EventRecord]:
    # Возвращает список событий, сохраненных в in-memory хранилище.
    return store.list_events()


@router.post(
    "/event",
    response_model=EventAcceptedResponse | EventRejectedResponse,
    summary="Принять и обработать событие",
)
async def post_event(
    event: EventRequest,
    event_service: EventService = Depends(get_event_service),
) -> EventAcceptedResponse | EventRejectedResponse:
    # Принимает событие и запускает полный пайплайн обработки.
    accepted, detail = await event_service.process_event(event)

    if not accepted:
        return EventRejectedResponse(
            status="duplicate", event_id=event.event_id, detail=detail
        )
    return EventAcceptedResponse(
        status="accepted", event_id=event.event_id, detail=detail
    )


@router.post(
    "/events/random",
    response_model=EventAcceptedResponse,
    summary="Сгенерировать случайное событие",
)
async def post_random_event(
    event_service: EventService = Depends(get_event_service),
) -> EventAcceptedResponse:
    # Генерирует случайное событие и отправляет его в обработку.
    try:
        event = event_service.generate_random_event()
        _, detail = await event_service.process_event(event)
    except RuntimeError:
        logger.exception("Случайное событие недоступно")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Сервис не может сгенерировать событие",
        )
    return EventAcceptedResponse(
        status="accepted", event_id=event.event_id, detail=detail
    )
