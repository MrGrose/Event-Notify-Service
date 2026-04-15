import logging
import json
import random
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import ValidationError

from app.models import EventRecord, EventRequest, EventType
from app.service.notification_svc import NotificationService
from app.store import InMemoryEventStore
from app.config.config import settings

logger = logging.getLogger(__name__)


class EventService:
    def __init__(
        self,
        store: InMemoryEventStore,
        notification_generator: NotificationService,
    ) -> None:
        self._store = store
        self._notification_generator = notification_generator
        self._event_templates = self._load_event_templates()

    # Обрабатывает событие и отправляет уведомление пользователю.
    async def process_event(self, event: EventRequest) -> tuple[bool, str]:
        record = EventRecord(
            event_id=event.event_id,
            user_id=event.user_id,
            type=event.type,
            payload=event.payload.model_dump(exclude_none=True),
        )
        is_new = self._store.save_if_new(record)
        if not is_new:
            logger.info("Дубликат события пропущен: event_id=%s", event.event_id)
            return False, "Событие уже было обработано ранее."

        notification_text = await self._notification_generator.generate(event)
        self._store.set_notification_text(event.event_id, notification_text)
        logger.info(
            "Уведомление отправлено: user_id=%s event_id=%s text=%s",
            event.user_id,
            event.event_id,
            notification_text,
        )
        return True, "Событие обработано успешно."

    # Генерирует случайное событие для endpoint /random-event.
    def generate_random_event(self) -> EventRequest:
        if not self._event_templates:
            raise RuntimeError("Нет валидных шаблонов в data/")
        template = random.choice(self._event_templates)
        event_type = EventType(template["type"])
        payload = template["payload"]
        user_id = str(template["user_id"])

        return EventRequest(
            event_id=uuid4(),
            user_id=user_id,
            type=event_type,
            payload=payload,
        )

    # Загружает шаблоны событий для random-event из JSON файла.
    def _load_event_templates(self) -> list[dict[str, Any]]:
        path = Path(settings.path_event)
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            logger.warning("Не удалось прочитать из data/")
            return []

        if not isinstance(raw, list):
            return []
        valid_templates = []
        for item in raw:
            try:
                event = EventRequest.model_validate(item)
                valid_templates.append(
                    {
                        "user_id": event.user_id,
                        "type": event.type.value,
                        "payload": event.payload.model_dump(exclude_none=True),
                    }
                )
            except ValidationError:
                continue
        return valid_templates
