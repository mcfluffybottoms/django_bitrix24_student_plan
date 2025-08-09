"""
URL configuration for task1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from main.views.main import start, returnstart

app_name = "main"

urlpatterns = [
    path('', start, name='start'),
    path('return', returnstart, name='returnstart'),
    path('task1/', include('task1.urls')),
    path('task2/', include('task2.urls')),
    path('task3/', include('task3.urls')),
    path('task4/', include('task4.urls')),
    path('task5/', include('task5.urls')),
]
