from django.contrib import admin
from .models import CityName, CityWeather, UserSubscription

admin.site.register(CityName)
admin.site.register(CityWeather)
admin.site.register(UserSubscription)
