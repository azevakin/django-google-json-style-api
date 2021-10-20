from typing import Generic, Optional, TypeVar, Union

from pydantic import BaseModel, ValidationError as PydanticValidationError

from django.core.exceptions import BadRequest, ObjectDoesNotExist, PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404

from django_google_json_style_api.base import (
    CamelModel,
    GenericCamelModel,
    get_request_id,
    logger,
)
from django_google_json_style_api.exceptions import Unauthorized

__all__ = [
    "BaseResponse",
    "BaseResponseData",
    "BaseSuccessResponse",
    "BaseEmptySuccessResponse",
    "ErrorResponse",
    "DEFAULT_API_VERSION",
]

ItemT = TypeVar("ItemT")
DataT = TypeVar("DataT")

DEFAULT_API_VERSION = "1.0"


class BaseResponseData(GenericCamelModel, Generic[ItemT]):
    """Базовая часть ответа для типизации поля data"""

    kind: Optional[str]
    current_item_count: int
    items_per_page: int
    start_index: int
    total_items: int
    items: list[ItemT]


class BaseResponse(CamelModel):
    """Базовый ответ"""

    api_version: Optional[str]
    id: Optional[str]


class BaseSuccessResponse(BaseResponse, GenericCamelModel, Generic[DataT]):
    """Базовый успешный ответ"""

    __kind__: str
    __data_class__ = BaseResponseData

    data: DataT

    @classmethod
    def make_from(
        cls,
        request: WSGIRequest,
        *,
        total_items: int,
        items: list[ItemT],
        items_per_page: int = 100,
        start_index: int = 0,
        **kwargs,
    ) -> "BaseSuccessResponse":
        """
        Фабричный метод создания ответа
        :param request:
        :param total_items: Итоговое количество записей
        :param items: Записи страницы
        :param items_per_page: Количество записей на странице
        :param start_index: Начальный индекс страницы
        :param kwargs: Дополнительные параметры
        :return: Экземпляр успешного ответа
        """
        request_id = get_request_id(request)
        data = cls.__data_class__(
            kind=cls.__kind__,
            current_item_count=len(items or []),
            items_per_page=items_per_page,
            start_index=start_index,
            total_items=total_items,
            items=items,
            **kwargs,
        )
        return cls(id=request_id, data=data)


class BaseEmptySuccessResponse(BaseResponse):
    """Базовый успешный ответ с предопределенным значением data.
    В data всегда status: ok"""

    data: dict

    @classmethod
    def make_from(cls, request: WSGIRequest) -> "BaseEmptySuccessResponse":
        """
        Фабричный метод создания успешного ответа
        :param request:
        :return: Экземпляр успешного ответа
        """
        data = {"status": "OK"}
        return cls(id=get_request_id(request), data=data)


class ErrorsItem(BaseModel):
    """Элемент ошибки"""

    reason: str
    location: Optional[str]
    message: str


class Error(BaseModel):
    """Данные об ошибке"""

    code: int
    errors: list[ErrorsItem]


class ErrorResponse(BaseResponse, BaseModel):
    """Ответ с ошибкой"""

    error: Error

    @classmethod
    def make_from(
        cls,
        *,
        request: WSGIRequest,
        exception: Union[Exception, str],
        default_status_code: int = 500,
    ) -> ("ErrorResponse", int):
        """
        Фабричный метод создания ответа с ошибкой
        :param request: Запрос
        :param exception: Исключение или Ошибка
        :param default_status_code: Код статуса ответа по-умолчанию
        :return: Экземпляр ответа с ошибкой
        """
        request_id = get_request_id(request)
        message = "Unknown error"
        reason = "Unknown"
        status_code = default_status_code
        errors = []

        if isinstance(exception, str):
            message = exception
        elif isinstance(exception, Exception):
            message = str(exception)
            reason = exception.__class__.__name__
            if isinstance(exception, PydanticValidationError):
                status_code = 400
                errors = cls._make_errors_from_pydantic_validation_error(
                    validation_error=exception
                )
            elif isinstance(exception, BadRequest):
                status_code = 400
            elif isinstance(exception, (ObjectDoesNotExist, Http404)):
                status_code = 404
            elif isinstance(exception, PermissionDenied):
                status_code = 403
            elif isinstance(exception, Unauthorized):
                status_code = 401

        if not errors:
            errors.append(ErrorsItem(reason=reason, message=message))

        error = Error(code=status_code, errors=errors)
        return cls(id=request_id, error=error), status_code

    @staticmethod
    def _make_errors_from_pydantic_validation_error(
        validation_error: PydanticValidationError,
    ) -> list[ErrorsItem]:
        errors = []
        reason = validation_error.__class__.__name__
        for error in validation_error.errors():
            try:
                locations = error["loc"]
                msg = error["msg"]
            except (KeyError, AssertionError):
                logger.exception("Incompatible Pydantic error")
                # Если формат ошибки изменился, возьмем текст ошибки из исключения
                errors.append(
                    ErrorsItem(
                        reason=reason,
                        message=str(validation_error),
                    )
                )
                break
            for location in locations:
                errors.append(
                    ErrorsItem(
                        reason=reason,
                        location=location,
                        message=msg,
                    )
                )
        return errors
