from django.urls import path
from . import views
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('subscriptions/all/', views.UserSubscriptionsView.as_view(), name='subscriptions_list'),
    path('subscriptions/new/', views.NewSubscriptionView.as_view(), name='new_subscription'),
    path('subscriptions/<int:subscr_id>/', views.SubscriptionActionsView.as_view(), name='new_subscription'),
]