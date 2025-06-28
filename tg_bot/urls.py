from django.urls import path
from . import bot
from .views import abot_index,mobile_done_cart, cart_webapp, webapp_callback

urlpatterns = [
    path('webhook/', bot.webhook, name='webhook'),
    path('abot_index/<int:order_id>', abot_index, name='abot_index'),
    path('mobile_done_cart/<int:order_id>', mobile_done_cart, name='mobile_done_cart'),
    path('cart/<int:order_id>/', cart_webapp, name='cart_webapp'),
    path('webapp/callback/', webapp_callback, name='webapp_callback'),
]