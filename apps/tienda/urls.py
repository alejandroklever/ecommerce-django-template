from django.contrib.auth.decorators import login_required
from django.urls import path

from apps.tienda.views import (MostrarTienda, EditarTienda, CrearProducto, EditarProducto, EliminarProducto)

app_name = 'tienda'

urlpatterns = [
    path('', login_required(MostrarTienda.as_view()), name='mostrar-tienda'),
    path('editar/<int:pk>', login_required(EditarTienda.as_view()), name='editar-tienda'),
    path('producto/crear', CrearProducto.as_view(), name='crear-producto'),
    path('producto/editar/<int:pk>', EditarProducto.as_view(), name='editar-producto'),
    path('producto/delete/<int:pk>', EliminarProducto.as_view(), name='borrar-producto'),
]
