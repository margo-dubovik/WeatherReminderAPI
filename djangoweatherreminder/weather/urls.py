from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from . import views


urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('auth/', include('users.urls')),
    path('subscriptions/all/', views.UserSubscriptionsView.as_view(), name='subscriptions_list'),
    path('subscriptions/new/', views.NewSubscriptionView.as_view(), name='new_subscription'),
    path('subscriptions/<int:id>/', views.SubscriptionActionsView.as_view(), name='subscription_action'),
]
