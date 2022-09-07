from django.db import models
from django.contrib.auth.models import User


class CityName(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=150)
    country = models.CharField(max_length=150)
    region = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.name}, {self.region}, {self.country}"


class CityWeather(models.Model):
    city = models.ForeignKey(CityName, on_delete=models.CASCADE, related_name="weather")
    last_info_update = models.DateTimeField(auto_now=True)
    weather_description = models.CharField(max_length=200)
    temperature = models.FloatField()
    feels_like = models.FloatField()
    humidity = models.FloatField()
    pressure = models.FloatField()
    visibility = models.FloatField()
    wind_speed = models.FloatField()
    clouds = models.FloatField()
    rain = models.FloatField()
    snow = models.FloatField()

    def __str__(self):
        return f"city {self.city}, weather: {self.weather_description}, {self.temperature}°C, " \
               f" last update on {self.last_info_update}"


class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    city = models.ForeignKey(CityName, on_delete=models.CASCADE, related_name="subscriptions")
    weather_info = models.ForeignKey(CityWeather, on_delete=models.CASCADE, related_name="subscriptions", null=True)
    notification_frequency = models.IntegerField()
    last_info_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"user {self.user}, city {self.city.name}, notify every {self.notification_frequency}h, " \
               f"last update on {self.last_info_update}"
