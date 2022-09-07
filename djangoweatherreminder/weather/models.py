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
    temperature = models.IntegerField()
    feels_like = models.IntegerField()
    humidity = models.IntegerField()
    pressure = models.IntegerField()
    visibility = models.IntegerField()
    wind_speed = models.IntegerField()
    clouds = models.IntegerField()
    rain = models.IntegerField()
    snow = models.IntegerField()

    def __str__(self):
        return f"city {self.city}, weather: {self.weather_description}, {self.temperature}°C, " \
               f"feels_like {self.feels_like}°C, humidity {self.humidity}%, pressure {self.pressure}hPa," \
               f"visibility {self.visibility}m, wind speed {self.wind_speed}m/sec, cloudiness {self.clouds} %," \
               f"rain volume for the last 1 hour {self.rain}mm, snow volume for the last 1 hour {self.snow}mm," \
               f" last update on {self.last_info_update}"


class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    city = models.ForeignKey(CityName, on_delete=models.CASCADE, related_name="subscriptions")
    weather_info = models.ForeignKey(CityWeather, on_delete=models.CASCADE, related_name="subscriptions", null=True)
    notification_frequency = models.IntegerField()
    last_info_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"user {self.user}, city {self.city}, notify every {self.notification_frequency}h, " \
               f"weather_info {self.weather_info}, last update on {self.last_info_update}"
