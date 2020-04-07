from django.contrib.auth.decorators import login_required
from django.urls import path

from apps.tienda.views import (MostrarTienda, EditarTienda, CrearProducto, EditarProducto, EliminarProducto,
                               ListarTiendasVista, VisitarTiendaVista, ListarProductosVista)

app_name = 'tienda'

urlpatterns = [
    path('', login_required(MostrarTienda.as_view()), name='mostrar-tienda'),
    path('editar/<int:pk>', login_required(EditarTienda.as_view()), name='editar-tienda'),
    path('productos/listar', ListarProductosVista.as_view(), name='listar-productos'),
    path('producto/crear', CrearProducto.as_view(), name='crear-producto'),
    path('producto/editar/<int:pk>', EditarProducto.as_view(), name='editar-producto'),
    path('producto/delete/<int:pk>', EliminarProducto.as_view(), name='borrar-producto'),
    path('listar', ListarTiendasVista.as_view(), name='listar-tiendas'),
    path('<int:tienda_id>/productos', VisitarTiendaVista.as_view(), name='visitar-tienda'),

]
