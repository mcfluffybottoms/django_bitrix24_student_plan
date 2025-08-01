from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.get_bitrix_user_token_from_header import \
    get_bitrix_user_token_from_header
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

from django.conf import settings

@main_auth(on_start=True, set_cookie=True)
def start(request):
    app_settings = settings.APP_SETTINGS
    return render(request, 'index.html', locals())

@main_auth(on_cookies=True)
def returnstart(request):
    app_settings = settings.APP_SETTINGS
    return render(request, 'index.html', locals())
