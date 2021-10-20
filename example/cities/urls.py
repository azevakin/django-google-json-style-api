from django.urls import path
from django.views.decorators import csrf

from . import views

urlpatterns = [
    path(
        "add/",
        csrf.csrf_exempt(views.AddCitiesView.as_view()),
        name="add-cities",
    ),
    path(
        "test-empty-success-response/",
        csrf.csrf_exempt(views.TestEmptySuccessView.as_view()),
        name="test-empty-success-response",
    ),
]
