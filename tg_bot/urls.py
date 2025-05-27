from django.urls import path
from . import bot

urlpatterns = [
    path('webhook/', bot.webhook, name='webhook'),
]
