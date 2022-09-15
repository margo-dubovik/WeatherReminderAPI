from celery import shared_task
from celery.schedules import crontab

from .models import CityName, CityWeather, UserSubscription
from .views import get_weather, validate_serializer
from .serializers import CityNameSerializer, CityWeatherSerializer



@shared_task()
def update_weather_table():
    all_cities = CityName.objects.all()
    for city in all_cities:
        # print("CITY:")
        city_weather = CityWeather.objects.get(city=city)
        city_data = CityNameSerializer(city).data
        # print(city_data)
        weather_data, code = get_weather(city_data)
        if code != 200:
            print({'error': weather_data['message'], 'code': code})
        else:
            city_weather_serializer = CityWeatherSerializer(instance=city_weather, data=weather_data, partial=True)
            if city_weather_serializer.is_valid():
                city_weather_serializer.save()
                # print("weather updated")
            else:
                print({'errors': city_weather_serializer.errors})
    print("weather updated")
