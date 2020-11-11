from django.urls import path

from apps.compra import views

app_name = 'compra'

urlpatterns = [
    path('carrito/', views.ListarPedidosVista.as_view(), name='listar-carrito'),
    path('editar/pedido/<int:pk>', views.EditarPedido.as_view(), name='editar-pedido'),
    path('eliminar/pedido/<int:pk>', views.EliminarPedido.as_view(), name='eliminar-pedido'),
    path('tienda/<int:tienda_id>/pagar/<int:pk>/<int:cantidad>', views.BankTransactionView.as_view(), name='pagar-pedido'),
    path('tienda/<int:tienda_id>/detalles/<int:pk>', views.DetalleProductosVista.as_view(), name='detalles-producto'),
]
