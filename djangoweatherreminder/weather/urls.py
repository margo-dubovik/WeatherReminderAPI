from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from . import views

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView



urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('subscriptions/all/', views.UserSubscriptionsView.as_view(), name='subscriptions_list'),
    path('subscriptions/new/', views.NewSubscriptionView.as_view(), name='new_subscription'),
    path('subscriptions/<int:id>/', views.SubscriptionActionsView.as_view(), name='subscription_action'),
]