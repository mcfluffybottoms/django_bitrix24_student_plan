from django.urls import path

from task2.views.task2 import product_page, start_task2, proxy_image

app_name = "task2"

urlpatterns = [
    path('<int:product_id>/', start_task2, name='get_task2'),
    path('', start_task2, name='start_task2'),
    path('item/<token>/', product_page, name='product_page'),
    path('image-proxy/', proxy_image, name='proxy_image'),
]
