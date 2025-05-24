from django.urls import path
from . import views


urlpatterns = [
    path('user/register', views.RegisterAPI.as_view()),
    path('user/login', views.LoginAPI.as_view()),
    path('user/token-lifetime', views.TokenLifetimeAPI.as_view()),
    path('user/refresh-token', views.RefreshTokenAPI.as_view()),
    path('user/profile/<str:method>', views.ProfileAPI.as_view()),
    path('user/verify-email', views.EmailVerificationAPI.as_view()),
    path('user/verify-otp', views.OTPVerificationAPI.as_view()),
    path('user/change-password', views.PwdChangeAPI.as_view()),
    path('user/request-otp', views.OTPRequestAPI.as_view()),
    path('countries', views.CountriesAPI.as_view()),
    path('cities', views.citiesAPI.as_view()),
]
