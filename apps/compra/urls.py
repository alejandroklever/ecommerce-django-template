from django.urls import path

from .views import index, ListarTiendasVista, VisitarTiendaVista

app_name = 'compra'

urlpatterns = [
    path('<int:pk>', index, name='comprar'),
    path('tiendas/listar/', ListarTiendasVista.as_view(), name='listar-tiendas'),
    path('tienda/<int:pk>/productos/', VisitarTiendaVista.as_view(), name='visitar-tienda')
]
