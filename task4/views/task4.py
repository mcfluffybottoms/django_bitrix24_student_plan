import json

from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from local_settings import YANDEX_API_KEY
from task4.models.models import Map


@main_auth(on_cookies=True)
def start_task4(request):
    but = request.bitrix_user_token
    locations = Map.get_map_locations(but, YANDEX_API_KEY)
    locations_json = json.dumps(locations, ensure_ascii=False)
    return render(request, 'task4.html', {"locations": locations_json, "api_key" : YANDEX_API_KEY})
