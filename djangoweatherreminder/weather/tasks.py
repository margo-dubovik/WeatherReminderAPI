from celery import shared_task
from celery.schedules import crontab
from datetime import datetime, timedelta
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

from .models import CityName, CityWeather, UserSubscription
from .views import get_weather, validate_serializer
from .serializers import CityNameSerializer, CityWeatherSerializer, UserSubscriptionSerializer


def update_weather_table():
    all_cities = CityName.objects.all()
    for city in all_cities:
        city_weather = CityWeather.objects.get(city=city)
        city_data = CityNameSerializer(city).data
        weather_data, code = get_weather(city_data)
        if code != 200:
            print({'error': weather_data['message'], 'code': code})
        else:
            city_weather_serializer = CityWeatherSerializer(instance=city_weather, data=weather_data, partial=True)
            if city_weather_serializer.is_valid():
                city_weather_serializer.save()
            else:
                print({'errors': city_weather_serializer.errors})
    print("weather updated")


def send_email(weather_data, city_data, user):
    del weather_data['city']
    del weather_data['last_info_update']

    email_subject = "Weather report"
    email_body = render_to_string('weather/weather_report_template.html', {
        'weather_data': weather_data,
        'city_data': city_data,
    },)
    print("email body=", email_body)
    email = EmailMessage(
        subject=email_subject,
        body=email_body,
        from_email=settings.EMAIL_FROM_USER,
        to=[user.email]
    )
    email.send()
    print("email=", email)


def update_subscriptions_table():
    all_subscriptions = UserSubscription.objects.all()
    for subscription in all_subscriptions:
        time_delta = timezone.now() - subscription.last_info_update
        # if time_delta > timedelta(hours=subscription.notification_frequency):
        if time_delta > timedelta(minutes=subscription.notification_frequency):  # for testing convenience
            weather_data = CityWeatherSerializer(subscription.weather_info).data
            city_data = CityNameSerializer(subscription.city).data
            send_email(weather_data=weather_data, city_data=city_data, user=subscription.user)
            print("email sent!")
            new_data = {
                'last_info_update': timezone.now(),
            }
            subscription_serializer = UserSubscriptionSerializer(instance=subscription, data=new_data, partial=True)
            if subscription_serializer.is_valid():
                subscription_serializer.save()
            else:
                print({'errors': subscription_serializer.errors})
    print("all subscriptions updated")


@shared_task()
def update_tables_and_send_emails():
    update_weather_table()
    update_subscriptions_table()
    print("ALL TASKS COMPLETE")
