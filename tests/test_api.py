import unittest

from fastapi.testclient import TestClient

from app.main import app


class EventApiTests(unittest.TestCase):
    def setUp(self) -> None:
        # Поднимает тестовый клиент и lifespan для инициализации app.state.
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self) -> None:
        # Закрывает клиент и освобождает ресурсы приложения.
        self.client.__exit__(None, None, None)

    def test_post_event_accepts_valid_payload(self) -> None:
        # Проверяет, что валидное новое событие принимается.
        payload = {
            "event_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
            "user_id": "123",
            "type": "task_created",
            "payload": {
                "title": "Сделать отчёт",
                "description": "до пятницы",
            },
        }

        response = self.client.post("/event", json=payload)
        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["status"], "accepted")
        self.assertEqual(body["event_id"], payload["event_id"])

    def test_post_event_returns_duplicate_for_same_event_id(self) -> None:
        # Проверяет, что повторный event_id помечается как дубликат.
        payload = {
            "event_id": "6c1f9db3-1dc4-4f11-aad1-04f4d0d5647c",
            "user_id": "123",
            "type": "meeting_created",
            "payload": {
                "title": "Планерка",
                "time": "завтра 10:00",
            },
        }

        first = self.client.post("/event", json=payload)
        second = self.client.post("/event", json=payload)
        body = second.json()

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(body["status"], "duplicate")
        self.assertEqual(body["event_id"], payload["event_id"])

    def test_post_random_event_returns_accepted(self) -> None:
        # Проверяет, что /events/random возвращает accepted.
        response = self.client.post("/events/random")
        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["status"], "accepted")
        self.assertIn("event_id", body)


if __name__ == "__main__":
    unittest.main()
