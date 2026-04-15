import logging
import json
import httpx

from app.models import EventRequest, EventType
from app.config.config import settings
from app.config.prompts import CONTEXT

logger = logging.getLogger(__name__)


class NotificationService:
    # Генерирует короткий текст через llm
    async def generate(self, event: EventRequest) -> str:
        if llm_text := await self._try_generate_with_ollama(event):
            return llm_text
        fallback_text = self._fallback_text(event)
        logger.info("Использован текст: %s", fallback_text)
        return fallback_text

    # Пытается получить текст уведомления из Ollama.
    async def _try_generate_with_ollama(self, event: EventRequest) -> str | None:
        prompt = self._build_prompt(event)
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": settings.ollama_temperature,
                "num_predict": settings.ollama_num_predict,
            },
        }

        try:
            async with httpx.AsyncClient(
                timeout=settings.llm_timeout_seconds
            ) as client:
                response = await client.post(
                    f"{settings.ollama_url}/api/generate", json=payload
                )
                response.raise_for_status()
                data = response.json()
                text = str(data.get("response", "")).strip()
                logger.info("Сгенерирован текст: %s", text)
                return text or None
        except (httpx.HTTPError, ValueError) as e:
            logger.warning("LLM недоступна: %s", e)
            return None

    # Собирает промпт из общего шаблона с примерами.
    def _build_prompt(self, event: EventRequest) -> str:
        payload_json = json.dumps(
            event.payload.model_dump(exclude_none=True), ensure_ascii=False
        )
        return CONTEXT.replace("{type}", event.type.value).replace(
            "{payload}", payload_json
        )

    # Формирует шаблонный текст, если LLM недоступна.
    def _fallback_text(self, event: EventRequest) -> str:
        payload = event.payload
        if event.type == EventType.TASK_CREATED:
            title = payload.title or "Новая задача"
            description = payload.description or "без деталей"
            return f"Новая задача: {title} ({description})."

        if event.type == EventType.MEETING_CREATED:
            title = payload.title or "Новая встреча"
            time = payload.time or payload.description or "время не указано"
            return f"Запланирована встреча: {title}, время: {time}."

        if event.type == EventType.MESSAGE_RECEIVED:
            sender = payload.sender or "неизвестный отправитель"
            text = payload.text or payload.description or "без текста"
            return f"Новое сообщение от {sender}: {text}."
        return "Новое сообщение, проверьте детали в вашем сервисе."
