from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample
import requests
import json

from .models import CityName, CityWeather, UserSubscription
from .serializers import CityNameSerializer, CityWeatherSerializer, UserSubscriptionSerializer, \
    OneSubscriptionSerializer

from dotenv import load_dotenv
import os

load_dotenv()


def get_weather(city_data):
    OWM_TOKEN = os.environ.get('OWM_TOKEN')
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_data['name']},{city_data['state']}," \
          f"{city_data['country_code']}&appid={OWM_TOKEN}&units=metric"
    weather_resp = requests.get(url).json()

    if weather_resp['cod'] != 200:
        res = {'message': weather_resp['message']}
        code = weather_resp['cod']
    else:
        res = {
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
        code = 200

    return res, code


def validate_serializer(serializer, error_message):
    if serializer.is_valid():
        serializer.save()
    else:
        return Response({'errors': serializer.errors,
                         'message': error_message},
                        status=status.HTTP_400_BAD_REQUEST)


def remove_unused_entries():
    cities = CityName.objects.all()
    for city in cities:
        city_subscriptions = city.subscriptions.all()
        if not city_subscriptions:
            city.delete()


class UserSubscriptionsView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(description='### Get the list of all your subscriptions', )
    def get(self, request):
        user = request.user
        subscriptions = user.subscriptions
        serializer = UserSubscriptionSerializer(subscriptions, many=True)
        for subscriprion in serializer.data:
            subscriprion.pop('user')
            subscriprion.pop('weather_info')
            subscriprion.pop('last_info_update')

            city_id = subscriprion['city']
            city = CityName.objects.get(id=city_id)
            city_info = CityNameSerializer(city)
            subscriprion['city'] = city_info.data

        return Response(serializer.data)


class NewSubscriptionView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OneSubscriptionSerializer

    @extend_schema(description='### Provide data for a new subscription.</br></br>'
                               '"city": name of the city you subscribe to.</br>'
                               '"state": available only for the USA locations. if not needed, just remove it.</br> '
                               '"country_code": a 2-letter ISO Alpha-2 code.</br>'
                               ' "notification_frequency": measured in hours.',
                   )
    def post(self, request):

        request_body = json.loads(request.body)

        city_data = request_body['city']

        weather_data, code = get_weather(city_data)
        if code != 200:
            return Response({'error': weather_data['message'],
                            'code': code},
                            status=status.HTTP_400_BAD_REQUEST)

        else:
            if not CityName.objects.filter(name=city_data['name'],
                                           state=city_data['state'],
                                           country_code=city_data['country_code']).exists():
                city_serializer = CityNameSerializer(data=city_data)
                validate_serializer(city_serializer, error_message="city_serializer errors:")

            subscription_city = CityName.objects.get(name=city_data['name'],
                                                     state=city_data['state'],
                                                     country_code=city_data['country_code'])

            if subscription_city.subscriptions.filter(user=request.user).exists():
                return Response({'error': 'You are already subscribed to this city. '
                                          'Please, edit an existing subscription'},
                                status=status.HTTP_400_BAD_REQUEST)

            if not CityWeather.objects.filter(city=subscription_city).exists():
                weather_data['city'] = subscription_city.pk
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

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return OneSubscriptionSerializer

    @extend_schema(description='### Write new updated information about your subscription.</br></br>'
                               '"city": name of the city you subscribe to.</br>'
                               '"state": available only for the USA locations. if not needed, just remove it.</br> '
                               '"country_code": a 2-letter ISO Alpha-2 code.</br>'
                               '"notification_frequency": measured in hours.',
                   )
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
            city_data = request_body['city']
            # if any field about city has changed
            if not CityName.objects.filter(name=city_data['name'],
                                           state=city_data['state'],
                                           country_code=city_data['country_code']).exists():
                city_serializer = CityNameSerializer(data=city_data)
                validate_serializer(city_serializer, error_message="city_serializer errors:")

            subscription_city = CityName.objects.get(name=city_data['name'],
                                                     state=city_data['state'],
                                                     country_code=city_data['country_code'])

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
                remove_unused_entries()  # remove cities that nobody is subscribed for
                return Response({"res": "Subscription edited"}, status=status.HTTP_200_OK)
            else:
                return Response({"res": subscription_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(description='### Specify the id of the subscription you want to delete',)
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
            remove_unused_entries()  # remove cities that nobody is subscribed for
            return Response(
                {"res": "Subscription deleted"},
                status=status.HTTP_200_OK
            )
