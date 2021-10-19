from django.utils.decorators import method_decorator
from django.views import View

from django_google_json_style_api.decorators import process_json_response

from .models import City
from .schemas import AddCitiesRequest, CityDataItem, CityResponse


@method_decorator(process_json_response(api_version="1.1"), name="dispatch")
class AddCitiesView(View):
    def post(self, request):
        cities = AddCitiesRequest.parse_raw(request.body).cities
        response_items = []
        for add_city_request in cities:
            city = City.objects.create(**add_city_request.dict())
            city_data_item = CityDataItem(id=city.id, city_name=city.city_name)
            response_items.append(city_data_item)
        return CityResponse.make_from(
            request,
            total_items=City.objects.count(),
            items=response_items,
        )
