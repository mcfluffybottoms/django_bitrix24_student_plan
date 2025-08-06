from datetime import datetime, timedelta

from django.shortcuts import render, redirect

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from task3.models.models import Employee


@main_auth(on_cookies=True)
def start_task4(request):
    but = request.bitrix_user_token.user
    username = but.first_name + " " + but.last_name;
    return render(request, 'task4.html', {"username": username})
