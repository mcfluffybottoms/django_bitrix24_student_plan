from django.contrib import admin
from django.urls import path, include

from task3.views.task3 import start_task3, workers

app_name = "task3"

urlpatterns = [
    path('', start_task3, name='start_task3'),
    path('workers', workers, name='workers'),
]
