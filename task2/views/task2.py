import urllib

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from integration_utils.vendors.telegram import InputFile
from local_settings import NGROK_URL
from task2.models.models import Product
import requests
from django.http import HttpResponse


@main_auth(on_cookies=True)
@require_http_methods(["GET", "POST"])
def start_task2(request):
    but = request.bitrix_user_token
    context = {
        "suggested_ids": Product.get_available_ids(request.bitrix_user_token)
    }
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        token = Product.generate_token(but, product_id)
        error = ""
        full_url = ""
        if not token:
            error = "Товара с таким ID нет."
            qr_code = False
        else:
            full_url = "{}/task2/item/{}/".format(
                NGROK_URL.rstrip('/'),
                token
            )
            qr_code = True
        context["error"] = error
        context["qr_code"] = qr_code
        context["link"] = full_url
    return render(request, 'task2.html', context)


def product_page(request, token):
    product = Product.get_site_from_link(token)
    context = {'product': product}
    if product.get("IMG"):
        context['IMG'] = product['IMG']
        return render(request, 'product.html', context)

    return render(request, 'product.html', {'product': product})


def proxy_image(request):
    img_url = request.GET.get('url', '')
    req = urllib.request.Request(img_url)
    response = urllib.request.urlopen(req)
    return HttpResponse(response.read(), content_type=response.headers.get('Content-Type', 'image/png'))
