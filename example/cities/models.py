from django.db import models


class City(models.Model):
    city_name = models.TextField()
