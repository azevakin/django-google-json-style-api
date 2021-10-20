import uuid

from django.test import TestCase
from django.urls import reverse


class TestAddCities(TestCase):
    """
    This test covers:
        * decorator
        * CamelModel
        * GenericCamelModel
        * BaseResponse
        * BaseResponseData
    """

    def test_add_cities(self):
        url = reverse("add-cities")
        data = {
            "cities": [
                {"cityName": "Tyumen"},
                {"cityName": "Moscow"},
            ]
        }
        request_id = uuid.uuid4()
        response = self.client.post(
            url, data, content_type="application/json", request_id=request_id
        )
        response_json = response.json()
        response_json.pop("id")
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

    def test_failed_add_cities_request(self):
        """This test covers bad request"""
        url = reverse("add-cities")
        data = {
            "cities": None,
        }
        response = self.client.post(url, data, content_type="application/json")
        response_json = response.json()
        response_json.pop("id")
        self.assertDictEqual(
            response_json,
            {
                "apiVersion": "1.1",
                "error": {
                    "code": 400,
                    "errors": [
                        {
                            "location": "cities",
                            "message": "none is not an allowed value",
                            "reason": "ValidationError",
                        }
                    ],
                },
            },
        )
