# Django Google JSON Style API

Implementation of Google JSON Style Guide for Django

----
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![autoflake: on](https://img.shields.io/badge/autoflake-on-brightgreen)](https://github.com/myint/autoflake)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI](https://img.shields.io/pypi/v/django-google-json-style-api)](https://pypi.org/project/django-google-json-style-api/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-google-json-style-api)](https://pypi.org/project/django-google-json-style-api/)
---
## Install

    pip install django-google-json-style-api

## Example

    # models.py

    from django.db import models


    class City(models.Model):
        city_name = models.TextField()

    # schemas.py

    from typing import List

    from pydantic import BaseModel

    from django_google_json_style_api.base import CamelModel
    from django_google_json_style_api.responses import BaseResponseData, BaseSuccessResponse


    class AddCityRequest(CamelModel):
        city_name: str


    class AddCitiesRequest(BaseModel):
        cities: List[AddCityRequest]


    class CityDataItem(CamelModel):
        id: int
        city_name: str


    class CityResponseData(BaseResponseData[CityDataItem]):
        ...


    class CityResponse(BaseSuccessResponse[CityResponseData]):
        __kind__ = "City"

    # urls.py

    from django.urls import path
    from django.views.decorators import csrf

    from . import views

    urlpatterns = [
        path(
            "add/",
            csrf.csrf_exempt(views.AddCitiesView.as_view()),
            name="add-cities",
        ),
    ]


    # views.py

    from django_google_json_style_api.decorators import process_json_response

    from django.utils.decorators import method_decorator
    from django.views import View

    from .models import City
    from .schemas import AddCitiesRequest, CityResponse, CityDataItem


    @method_decorator(process_json_response(api_version='1.1'), name="dispatch")
    class AddCitiesView(View):
        def post(self, request):
            cities = AddCitiesRequest.parse_raw(request.body).cities
            response_items = []
            for add_city_request in cities:
                city = City.objects.create(**add_city_request.dict())
                city_data_item = CityDataItem(
                    id=city.id,
                    city_name=city.city_name
                )
                response_items.append(city_data_item)
            return CityResponse.make_from(
                request,
                total_items=City.objects.count(),
                items=response_items,
            )

    # tests.py

    from django.test import TestCase
    from django.urls import reverse


    class TestCities(TestCase):

        def test_add_cities(self):
            url = reverse('add-cities')
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
                    'apiVersion': '1.1',
                    "data": {
                        'currentItemCount': 2,
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
                        'itemsPerPage': 100,
                        'kind': 'City',
                        'startIndex': 0,
                        'totalItems': 2,
                    },
                }
            )


## TODO:

Docs, tests
