import logging
import uuid

from pydantic import BaseModel
from pydantic.generics import GenericModel

from django.core.handlers.wsgi import WSGIRequest

__all__ = ["CamelModel", "GenericCamelModel", "get_request_id", "logger"]


logger = logging.getLogger("django_google_json_style_api")
logger.addHandler(logging.NullHandler())


def get_request_id(request: WSGIRequest) -> str:
    """Получает request_id из запроса.
    Если request_id не задан, генерирует его методом uuid4"""
    return getattr(request, "request_id", None) or str(uuid.uuid4())


def _snake_to_camel(string: str) -> str:
    """Перводит snake_case в camelCase"""
    if not string:
        return string
    return "".join(
        index and word.capitalize() or word
        for index, word in enumerate(string.split("_"))
    )


class CamelModel(BaseModel):
    """Модель с переводом полей в camelCase"""

    class Config:
        alias_generator = _snake_to_camel
        allow_population_by_field_name = True


class GenericCamelModel(CamelModel, GenericModel):
    """Generic модель с переводом полей в camelCase"""
