from threading import Lock
from uuid import UUID

from app.models import EventRecord


class InMemoryEventStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._events: dict[UUID, EventRecord] = {}

    # Сохраняет событие только один раз по event_id.
    def save_if_new(self, event: EventRecord) -> bool:
        with self._lock:
            if event.event_id in self._events:
                return False
            self._events[event.event_id] = event
            return True

    # Обновляет текст уведомления у сохраненного события.
    def set_notification_text(self, event_id: UUID, text: str) -> None:
        with self._lock:
            event = self._events.get(event_id)
            if event is None:
                return
            event.notification_text = text

    # Возвращает все сохраненные события из памяти.
    def list_events(self) -> list[EventRecord]:
        with self._lock:
            return list(self._events.values())