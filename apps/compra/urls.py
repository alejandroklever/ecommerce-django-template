from django.urls import path

from .views import index

app_name = 'compra'

urlpatterns = [
    path('<int:pk>', index, name='comprar')
]
