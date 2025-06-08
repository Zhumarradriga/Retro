from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from games import views

urlpatterns = [
    path('', views.home, name='home'),
    path('play/<slug:game_slug>/', views.play_game, name='play_game'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('save_score/', views.save_score, name='save_score'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register_view'),
    path('logout/', views.logout_view, name='logout'),
    path('api/', include('games.urls_api')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)