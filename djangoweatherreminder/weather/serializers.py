from rest_framework import serializers

from .models import CityName, CityWeather, UserSubscription


class CityNameSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=150)
    state = serializers.CharField(max_length=150, allow_blank=True)
    country_code = serializers.CharField(max_length=2)

    class Meta:
        model = CityName
        fields = ['name', 'state', 'country_code', ]


class CityWeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityWeather
        fields = ['city', 'last_info_update', 'weather_description', 'temperature', 'feels_like',
                  'humidity', 'pressure', 'visibility', 'wind_speed', 'clouds', 'rain', 'snow', ]


class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'city', 'weather_info', 'notification_frequency', 'last_info_update', ]


class OneSubscriptionSerializer(serializers.ModelSerializer):
    city = CityNameSerializer()
    notification_frequency = serializers.IntegerField()

    class Meta:
        model = UserSubscription
        fields = ['city', 'notification_frequency', ]