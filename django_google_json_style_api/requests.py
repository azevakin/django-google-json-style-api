from django_google_json_style_api.base import CamelModel

__all__ = [
    "PaginatedRequest",
]


class PaginatedRequest(CamelModel):
    """Запрос по постраничную отдачу данных"""

    items_per_page: int
    start_index: int = 0
