from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CityName, CityWeather, UserSubscription
from .serializers import CityNameSerializer, CityWeatherSerializer, UserSubscriptionSerializer
from rest_framework.permissions import IsAuthenticated


class UserSubscriptionsView(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        subscriptions = UserSubscription.objects.filter(user=user)
        serializer = UserSubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)
