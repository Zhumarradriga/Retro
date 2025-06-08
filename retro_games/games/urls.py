from django.urls import path
from . import views

app_name = 'games'  # Пространство имен

urlpatterns = [
    path('', views.home, name='home'),
    path('game/<slug:game_slug>/', views.game_detail, name='game_detail'),
    path('play/<slug:game_slug>/', views.play_game, name='play_game'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('save_score/', views.save_score, name='save_score'),
]