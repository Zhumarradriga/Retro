from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
]