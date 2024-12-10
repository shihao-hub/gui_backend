__all__ = ["HelloTest"]

from django.test import TestCase
from ninja.testing import TestClient

from apps.api.viewsets.exercise import router


class HelloTest(TestCase):
    def test_startup(self):
        client = TestClient(router)

        # hello
        response = client.get("hello")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"msg": "Hello World"})
