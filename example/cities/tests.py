from django.test import TestCase
from django.urls import reverse


class TestCities(TestCase):
    def test_add_cities(self):
        url = reverse("add-cities")
        data = {
            "cities": [
                {"cityName": "Tyumen"},
                {"cityName": "Moscow"},
            ]
        }
        response = self.client.post(url, data, content_type="application/json")
        response_json = response.json()
        self.assertDictEqual(
            response_json,
            {
                "apiVersion": "1.1",
                "data": {
                    "currentItemCount": 2,
                    "items": [
                        {
                            "id": 1,
                            "cityName": "Tyumen",
                        },
                        {
                            "id": 2,
                            "cityName": "Moscow",
                        },
                    ],
                    "itemsPerPage": 100,
                    "kind": "City",
                    "startIndex": 0,
                    "totalItems": 2,
                },
            },
        )
