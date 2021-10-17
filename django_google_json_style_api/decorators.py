from functools import wraps
from typing import Union

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from django_google_json_style_api.base import logger
from django_google_json_style_api.responses import (
    DEFAULT_API_VERSION,
    BaseResponse,
    ErrorResponse,
)


def process_json_response(
    function=None, api_version: str = DEFAULT_API_VERSION, **decorator_kwargs
):
    """Декоратор для вьюх.
    Перехватывает ошибки и формирует JSON ответа"""

    def _process_response_decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            exclude_none = decorator_kwargs.get("exclude_none", True)
            try:
                response = view_func(request, *args, **kwargs)
                return _make_json_response(
                    api_version, response, exclude_none=exclude_none
                )
            except Exception as e:
                logger.exception(e)
                return _make_error_response(
                    api_version, request, e, exclude_none=exclude_none
                )

        return _wrapped_view

    if function:
        return _process_response_decorator(function)
    return _process_response_decorator


def _make_error_response(
    api_version: str,
    request: WSGIRequest,
    exception: Union[str, Exception],
    *,
    default_status_code: int = 500,
    exclude_none,
) -> JsonResponse:
    response, status = ErrorResponse.make_from(
        request=request,
        exception=exception,
        default_status_code=default_status_code,
    )
    return _make_json_response(
        api_version, response, status=status, exclude_none=exclude_none
    )


def _make_json_response(
    api_version: str, response: BaseResponse, *, status=200, exclude_none
) -> JsonResponse:
    response.api_version = api_version
    return JsonResponse(
        response.dict(by_alias=True, exclude_none=exclude_none), status=status
    )
