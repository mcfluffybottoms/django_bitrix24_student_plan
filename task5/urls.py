from django.urls import path

from task5.views.task5 import start_task5
from task5.views.task5 import download

app_name = "task5"

urlpatterns = [
    path('', start_task5, name='start_task5'),
    path('download', download, name='download'),
]
