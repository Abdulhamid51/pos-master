from django.urls import path
from . import bot
from .views import abot_index,mobile_done_cart

urlpatterns = [
    path('webhook/', bot.webhook, name='webhook'),
    path('abot_index/<int:chat_id>', abot_index, name='abot_index'),
    path('mobile_done_cart', mobile_done_cart, name='mobile_done_cart')
]