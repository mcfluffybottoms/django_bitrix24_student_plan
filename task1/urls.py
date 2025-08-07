from django.contrib import admin
from django.urls import path, include

from main.views.main import returnstart
from task1.views.task1 import start_task1, top_task1, add_delivery

app_name = "task1"

urlpatterns = [
    path('', start_task1, name='start_task1'),
    path('top', top_task1, name='top_task1'),
    path('add', add_delivery, name='add_delivery'),
]
