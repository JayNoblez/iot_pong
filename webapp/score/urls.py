from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('log_game/', views.log_game, name='log_game'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('scoreboard/', views.scoreboard, name='scoreboard'),
]
