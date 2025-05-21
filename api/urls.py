from django.urls import path
from . import views


urlpatterns = [
    path('user/register', views.RegisterAPI.as_view()),
    path('user/login', views.LoginAPI.as_view()),
    path('user/token-lifetime', views.TokenLifetimeAPI.as_view()),
]
