from datetime import datetime, timedelta

from django.shortcuts import render, redirect

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from task3.models.models import Employee


@main_auth(on_cookies=True)
def start_task3(request):
    but = request.bitrix_user_token.user
    username = but.first_name + " " + but.last_name;
    return render(request, 'task3.html', {"username": username})


@main_auth(on_cookies=True)
def workers(request):
    but = request.bitrix_user_token
    generated_calls = []
    if request.method == "POST":
        number_of_calls = int(request.POST.get("number_of_calls"))
        old = request.POST.get("old") == "on"
        end_time = None
        if old:
            end_time = datetime.now() - timedelta(hours=25)
        print(old)
        print(end_time)
        generated_calls = Employee.debug_generate_calls(but, number=number_of_calls, end_time=end_time)
    employees = Employee.get_employee_list(but)
    context = {
        "employees": employees,
        "generated_calls": generated_calls
    }
    return render(request, 'workers.html', context)
