from django.urls import path
from . import bot
from .views import abot_index,mobile_done_cart, debtor_orders,add_to_cart,remove_from_cart,debtor_order_detail

urlpatterns = [
    path('webhook/', bot.webhook, name='webhook'),
    path('abot_index/<str:chat_id>', abot_index, name='abot_index'),
    path('mobile_done_cart/<str:chat_id>', mobile_done_cart, name='mobile_done_cart'),
    path('debtor_orders/<str:chat_id>', debtor_orders, name='debtor_orders'),
    path('add_to_cart/<str:chat_id>', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<str:chat_id>', remove_from_cart, name='remove_from_cart'),
    path('debtor_order_detail/<int:order_id>/<str:chat_id>', debtor_order_detail, name='debtor_order_detail'),
]