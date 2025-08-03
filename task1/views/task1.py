from django.shortcuts import render, redirect

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from django.conf import settings

from task1.models.models import Delivery, DeliveryForm


@main_auth(on_cookies=True)
def start_task1(request):
    but = request.bitrix_user_token.user
    username = but.first_name + " " + but.last_name;
    return render(request, 'task1.html', {"username": username})

@main_auth(on_cookies=True)
def top_task1(request):
    but = request.bitrix_user_token
    deals = Delivery.get_10_delivery_list(but=but)
    return render(request, 'top.html', {"deals": deals})

@main_auth(on_cookies=True)
def add_delivery(request):
    if request.method == "POST":
        form = DeliveryForm(request.POST)
        if form.is_valid():
            but = request.bitrix_user_token
            Delivery.add_delivery(but, form.cleaned_data)
            return redirect("task1:top_task1")
    else:
        form = DeliveryForm()
    return render(request, "delivery_form.html", {"form": form})