from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample
import requests
import json

from .models import CityName, CityWeather, UserSubscription
from .serializers import CityNameSerializer, CityWeatherSerializer, UserSubscriptionSerializer

from dotenv import load_dotenv
import os

load_dotenv()


def get_weather(city_name, subscription_city_pk):
    OWM_TOKEN = os.environ.get('OWM_TOKEN')
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OWM_TOKEN}&units=metric"
    weather_resp = requests.get(url).json()

    weather_data = {
        'city': subscription_city_pk,
        'weather_description': weather_resp['weather'][0]['description'],
        'temperature': weather_resp['main']['temp'],
        'feels_like': weather_resp['main']['feels_like'],
        'humidity': weather_resp['main']['humidity'],
        'pressure': weather_resp['main']['pressure'],
        'visibility': weather_resp['visibility'],
        'wind_speed': weather_resp['wind']['speed'],
        'clouds': weather_resp.get('clouds', {}).get('all', 0),
        'rain': weather_resp.get('rain', {}).get('1h', 0),
        'snow': weather_resp.get('snow', {}).get('1h', 0),
    }

    return weather_data


def validate_serializer(serializer, error_message):
    if serializer.is_valid():
        serializer.save()
    else:
        print(error_message, serializer.errors)


class UserSubscriptionsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        subscriptions = user.subscriptions
        serializer = UserSubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)


class NewSubscriptionView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(description='### Provide data for a new subscription.</br></br>'
                               '"city": name of the city you subscribe to.</br>'
                               '"state": optional. if not needed, just remove it.</br> '
                               '"country_code": a 2-letter ISO Alpha-2 code.</br>'
                               ' "notification_frequency": measured in hours.',
                   examples=[OpenApiExample(
                       'Example 1',
                       value={
                           'name': 'Detroit',
                           'state': 'MI',
                           'country_code': 'US',
                           'notification_frequency': '2'},
                   )],
                   request=[
                       CityNameSerializer(many=True),
                   ])
    def post(self, request):

        request_body = json.loads(request.body)

        city_data = {
            'name': request_body['name'],
            'state': request_body.get('state', ''),
            'country_code': request_body['country_code'],
        }

        if not CityName.objects.filter(name=city_data['name']).exists():
            city_serializer = CityNameSerializer(data=city_data)
            validate_serializer(city_serializer, error_message="city_serializer errors:")

        subscription_city = CityName.objects.get(name=city_data['name'])

        if not CityWeather.objects.filter(city=subscription_city).exists():
            weather_data = get_weather(city_data['name'], subscription_city.pk)
            city_weather_serializer = CityWeatherSerializer(data=weather_data)
            validate_serializer(city_weather_serializer, error_message="city_weather_serializer errors:")

        subscription_weather = CityWeather.objects.get(city=subscription_city.pk)

        subscription_data = {
            'user': request.user.pk,
            'city': subscription_city.pk,
            'weather_info': subscription_weather.pk,
            'notification_frequency': request_body['notification_frequency'],
        }

        subscription_serializer = UserSubscriptionSerializer(data=subscription_data)
        if subscription_serializer.is_valid():
            subscription_serializer.save()
            return Response(subscription_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(subscription_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionActionsView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(description='### Write new updated information about your subscription.</br></br>'
                               '"city": name of the city you subscribe to.</br>'
                               '"state": optional. if not needed, just remove it.</br> '
                               '"country_code": a 2-letter ISO Alpha-2 code.</br>'
                               '"notification_frequency": measured in hours.',
                   examples=[OpenApiExample(
                       'Example 1',
                       value={
                           'city_data': {
                               'name': 'Detroit',
                               'state': 'MI',
                               'country_code': 'US',
                           },
                           'notification_frequency': '2'},
                   )],
                   request=[
                       CityNameSerializer(many=True),
                   ])
    def put(self, request, id):
        user = request.user
        user_subscriptions = user.subscriptions.all()
        subscription = get_object_or_404(UserSubscription, pk=id)
        if not subscription or subscription not in user_subscriptions:
            return Response({"res": f"Subscription with id={id} does not exist for this user"},
                            status=status.HTTP_400_BAD_REQUEST,
                            )
        else:
            request_body = json.loads(request.body)
            city_data = request_body['city_data']
            # if any field about city has changed
            if not CityName.objects.filter(name=city_data['name'],
                                           state=city_data['state'],
                                           country_code=city_data['country_code']).exists():
                city_serializer = CityNameSerializer(data=city_data)

                validate_serializer(city_serializer, error_message="city_serializer errors:")

            subscription_city = CityName.objects.get(name=city_data['name'])

            if not CityWeather.objects.filter(city=subscription_city).exists():
                weather_data = get_weather(subscription_city.name, subscription_city.pk)
                city_weather_serializer = CityWeatherSerializer(data=weather_data)
                validate_serializer(city_weather_serializer, error_message="city_weather_serializer errors:")

            subscription_weather = CityWeather.objects.get(city=subscription_city.pk)

            new_subscription_data = {
                'user': request.user.pk,
                'city': subscription_city.pk,
                'weather_info': subscription_weather.pk,
                'notification_frequency': request_body.get('notification_frequency',
                                                           subscription.notification_frequency),
            }

            subscription_serializer = UserSubscriptionSerializer(instance=subscription, data=new_subscription_data,
                                                                 partial=True)
            if subscription_serializer.is_valid():
                subscription_serializer.save()
                return Response({"res": "Subscription edited"}, status=status.HTTP_200_OK)
            else:
                return Response({"res": subscription_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        user = request.user
        user_subscriptions = user.subscriptions.all()
        subscription = get_object_or_404(UserSubscription, pk=id)
        if not subscription or subscription not in user_subscriptions:
            return Response({"res": f"Subscription with id={id} does not exist for this user"},
                            status=status.HTTP_400_BAD_REQUEST,
                            )
        else:
            user.subscriptions.remove(subscription)
            subscription.delete()
            return Response(
                {"res": "Subscription deleted"},
                status=status.HTTP_200_OK
            )
