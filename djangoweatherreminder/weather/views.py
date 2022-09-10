from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
import requests

from .models import CityName, CityWeather, UserSubscription
from .serializers import CityNameSerializer, CityWeatherSerializer, UserSubscriptionSerializer

from dotenv import load_dotenv
import os

load_dotenv()


class UserSubscriptionsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        subscriptions = user.subscriptions
        serializer = UserSubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)


class NewSubscriptionView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(description='post description',
                   parameters=[
                    CityNameSerializer,
                    OpenApiParameter("notification_frequency",
                                     required=True, type=int)
                   ])
    def post(self, request):
        city_data = {
            'name': request.POST['name'],
            'state': request.POST.get('state', ''),
            'country_code': request.POST['country_code'],
        }

        if not CityName.objects.filter(name=city_data['name']).exists():
            city_serializer = CityNameSerializer(data=city_data)
            if city_serializer.is_valid():
                city_serializer.save()
            else:
                print("city_serializer errors:", city_serializer.errors)

        subscription_city = CityName.objects.get(name=city_data['name'])

        OWM_TOKEN = os.environ.get('OWM_TOKEN')
        URL = f"https://api.openweathermap.org/data/2.5/weather?q={city_data['name']}&appid={OWM_TOKEN}&units=metric"
        weather_resp = requests.get(URL).json()

        weather_data = {
            'city': subscription_city.pk,
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

        if not CityWeather.objects.filter(city=weather_data['city']).exists():
            city_weather_serializer = CityWeatherSerializer(data=weather_data)
            if city_weather_serializer.is_valid():
                city_weather_serializer.save()
            else:
                print("city_weather_serializer errors:", city_weather_serializer.errors)

        subscription_weather = CityWeather.objects.get(city=subscription_city.pk)

        subscription_data = {
            'user': request.user.pk,
            'city': subscription_city.pk,
            'weather_info': subscription_weather.pk,
            'notification_frequency': request.POST['notification_frequency'],
        }

        subscription_serializer = UserSubscriptionSerializer(data=subscription_data)
        if subscription_serializer.is_valid():
            subscription_serializer.save()
            return Response(subscription_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(subscription_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionActionsView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, id):
        user = request.user
        user_subscriptions = user.subscriptions.all()
        subscription = get_object_or_404(UserSubscription, pk=id)
        if not subscription or subscription not in user_subscriptions:
            return Response({"res": f"Subscription with id={id} does not exist for this user"},
                            status=status.HTTP_400_BAD_REQUEST,
                            )
        else:
            changes = request.data.get('changes')
            new_data = {key: value for key, value in changes.items()}
            print("new_data=", new_data)
            subscription_serializer = UserSubscriptionSerializer(instance=subscription, data=new_data, partial=True)
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
