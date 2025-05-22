from django.urls import path
from . import views


urlpatterns = [
    path('user/register', views.RegisterAPI.as_view()),
    path('user/login', views.LoginAPI.as_view()),
    path('user/token-lifetime', views.TokenLifetimeAPI.as_view()),
    path('user/refresh-token', views.RefreshTokenAPI.as_view()),
    path('user/profile/<str:data_type>', views.ProfileAPI.as_view()),
]
