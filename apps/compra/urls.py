from django.urls import path

from .views import DetalleProductosVista, ListarPedidosVista

app_name = 'compra'


def foo():
    pass


urlpatterns = [
    path('carrito/', ListarPedidosVista.as_view(), name='listar-carrito'),
    path('tienda/<int:tienda_id>/detalles/<int:pk>', DetalleProductosVista.as_view(), name='detalles-producto'),
]
