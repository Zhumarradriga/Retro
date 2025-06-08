from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from games import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('games.urls')),  # Включаем маршруты games
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('api/', include('games.urls_api')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('cart/', include('cart.urls', namespace='cart')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)