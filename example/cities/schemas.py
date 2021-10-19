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
