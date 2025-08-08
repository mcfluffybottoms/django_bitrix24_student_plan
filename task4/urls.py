from django.urls import path

from task4.views.task4 import start_task4

app_name = "task4"

urlpatterns = [
    path('', start_task4, name='start_task4'),
]
