from django.test import TestCase
from django.urls import reverse


class TestBaseEmptySuccessResponse(TestCase):
    """
    This test covers:
        * decorator
        * CamelModel
        * BaseResponse
        * BaseEmptySuccessResponse
    """

    def test_add_cities(self):
        url = reverse("test-empty-success-response")
        response = self.client.get(url, content_type="application/json")
        response_json = response.json()
        response_json.pop("id")
        self.assertDictEqual(
            response_json,
            {
                "apiVersion": "1.1",
                "data": {
                    "status": "OK",
                },
            },
        )
