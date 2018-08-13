from django.urls import path

from . import views
from .models import Game
from .models import Player
import paho.mqtt.client as mqtt

urlpatterns = [
    path('', views.index, name='index'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('scoreboard/', views.scoreboard, name='scoreboard'),
]